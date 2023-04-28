package fr.ensicaen.eng.ntnu.mobai.injectionattackanalysis.camera

import android.Manifest
import android.content.pm.PackageManager
import android.util.Base64
import android.util.Base64OutputStream
import android.util.Log
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
import fr.ensicaen.eng.ntnu.mobai.injectionattackanalysis.CallPAD
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import kotlin.math.ceil


class Capture (
    previewView: PreviewView,
    appCompatActivity: AppCompatActivity,
    base64ArrayList: ArrayList<String>,
    frameAmount: Int = 2,
    frameLatency: Int = 3,
    fps: Double = 30.00) {

    private var _imageCapture: ImageCapture? = null
    private var _captureDelay: Double = calcCaptureDelay(fps, frameLatency)
    private var _view: PreviewView = previewView
    private var _appCompatActivity: AppCompatActivity = appCompatActivity
    private val _frameAmount: Int = frameAmount
    private var _cameraExecutor: ExecutorService
    private var _base64Images: ArrayList<String> = base64ArrayList

    private lateinit var _outputStream: ByteArrayOutputStream
    private lateinit var _outputBase64Stream: Base64OutputStream

    init {
        cameraPermission()
        setupCamera()
        _cameraExecutor = Executors.newSingleThreadExecutor()
    }

    companion object {
        private const val TAG = "CameraXGFG"
        private const val REQUEST_CODE_PERMISSIONS = 20
    }

    private fun calcCaptureDelay(fps: Double, frameLatency: Int): Double {
        return ((1.0 / fps) * frameLatency) * 1000
    }

    private fun cameraPermission() {
        if (ContextCompat.checkSelfPermission(
                _appCompatActivity,
                Manifest.permission.CAMERA
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                _appCompatActivity,
                arrayOf(Manifest.permission.CAMERA),
                REQUEST_CODE_PERMISSIONS
            )
        }
    }

    private fun setupCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(_appCompatActivity)
        cameraProviderFuture.addListener({
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(_view.surfaceProvider)
            }

            _imageCapture = ImageCapture.Builder().build()
            val cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA
            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    _appCompatActivity, cameraSelector, preview, _imageCapture
                )
            } catch (exc: Exception) {
                Log.e(TAG, "Use cade binding failed", exc)
            }
        }, ContextCompat.getMainExecutor(_appCompatActivity))
    }

    public fun launchFramesCapture(currentDelay: Long, onImagesCompleted: () -> Unit) {
        if (isAmountOfImagesCompleted()) {
            //callPAD.sendPADRequest()
            onImagesCompleted()
            return
        }
        val imageCapture = _imageCapture ?: return
        _outputStream = ByteArrayOutputStream()
        _outputBase64Stream = Base64OutputStream(_outputStream, Base64.NO_WRAP)
        val outputOption = ImageCapture.OutputFileOptions.Builder(_outputBase64Stream).build()
        Thread.sleep(currentDelay)
        imageCapture.takePicture(
            outputOption, ContextCompat.getMainExecutor(_appCompatActivity), callbackSaved(onImagesCompleted)
        )
    }

    private fun callbackSaved(onImagesCompleted: () -> Unit): ImageCapture.OnImageSavedCallback {
        return object : ImageCapture.OnImageSavedCallback {
            override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                _base64Images.add(_outputStream.toString())
                _outputStream.close()
                _outputBase64Stream.close()
                val msg = "Photo capture succeeded"
                Toast.makeText(_appCompatActivity.baseContext, msg, Toast.LENGTH_LONG).show()
                Log.d(TAG, msg)
                launchFramesCapture(ceil(_captureDelay).toLong(), onImagesCompleted)
            }

            override fun onError(exception: ImageCaptureException) {
                Log.e(TAG, "Photo capture failed: ${exception.message}", exception)
            }
        }
    }

    private fun isAmountOfImagesCompleted() = _base64Images.size + 1 > _frameAmount
}
