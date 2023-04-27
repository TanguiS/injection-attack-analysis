package fr.ensicaen.eng.ntnu.mobai.framescapturer

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Base64
import android.util.Base64OutputStream
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.io.ByteArrayOutputStream
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import kotlin.math.ceil

class FramesCapture : AppCompatActivity() {
    private var _imageCapture: ImageCapture? = null
    private lateinit var _cameraExecutor: ExecutorService
    private lateinit var _outputStream: ByteArrayOutputStream
    private lateinit var _outputBase64Stream: Base64OutputStream
    private var _captureDelay = 0.0
    private lateinit var _base64Images: ArrayList<String>

    companion object {
        private const val TAG = "CameraXGFG"
        private const val REQUEST_CODE_PERMISSIONS = 20
        private const val FRAME_LATENCY = 3
        private const val FRAME_PER_SECOND = 30.0
        private const val FRAME_AMOUNT = 2
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_camera)
        cameraPermission()
        setupCamera()
        _base64Images = ArrayList(FRAME_AMOUNT)
        _cameraExecutor = Executors.newSingleThreadExecutor()
        findViewById<Button>(R.id._captureBtn).setOnClickListener {
            launchFramesCapture(0)
        }
    }

    private fun cameraPermission() {
        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.CAMERA
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.CAMERA),
                REQUEST_CODE_PERMISSIONS
            )
        }
    }

    private fun setupCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
        cameraProviderFuture.addListener({
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(findViewById<PreviewView>(R.id._cameraView).surfaceProvider)
            }

            _imageCapture = ImageCapture.Builder().build()
            val cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA
            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    this, cameraSelector, preview, _imageCapture
                )
            } catch (exc: Exception) {
                Log.e(TAG, "Use cade binding failed", exc)
            }
        }, ContextCompat.getMainExecutor(this))
        _captureDelay = calcCaptureDelay()
    }

    private fun calcCaptureDelay(): Double {
        return ((1.0 / FRAME_PER_SECOND) * FRAME_LATENCY) * 1000
    }

    private fun launchFramesCapture(currentDelay: Long) {
        if (isAmountOfImagesCompleted()) {
            val callPAD = CallPAD(_base64Images[0], _base64Images[1])
            _base64Images.clear()
            callPAD.sendPADRequest()
            return
        }
        val imageCapture = _imageCapture ?: return
        _outputStream = ByteArrayOutputStream()
        _outputBase64Stream = Base64OutputStream(_outputStream, Base64.NO_WRAP)
        val outputOption = ImageCapture.OutputFileOptions.Builder(_outputBase64Stream).build()
        Thread.sleep(currentDelay)
        imageCapture.takePicture(
            outputOption, ContextCompat.getMainExecutor(this), callbackSaved()
        )
    }

    private fun isAmountOfImagesCompleted() = _base64Images.size + 1 > FRAME_AMOUNT

    private fun callbackSaved(): ImageCapture.OnImageSavedCallback {
        return object : ImageCapture.OnImageSavedCallback {
            override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                _base64Images.add(_outputStream.toString())
                _outputStream.close()
                _outputBase64Stream.close()
                val msg = "Photo capture succeeded"
                Toast.makeText(baseContext, msg, Toast.LENGTH_LONG).show()
                Log.d(TAG, msg)
                launchFramesCapture(ceil(_captureDelay).toLong())
            }

            override fun onError(exception: ImageCaptureException) {
                Log.e(TAG, "Photo capture failed: ${exception.message}", exception)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        _cameraExecutor.shutdown()
        _outputBase64Stream.close()
        _outputStream.close()
    }
}