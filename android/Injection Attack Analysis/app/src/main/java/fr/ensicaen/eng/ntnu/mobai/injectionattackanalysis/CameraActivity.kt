package fr.ensicaen.eng.ntnu.mobai.injectionattackanalysis

import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import fr.ensicaen.eng.ntnu.mobai.injectionattackanalysis.camera.Capture

class CameraActivity : AppCompatActivity() {
    private var _base64ImgList = ArrayList<String>(FRAME_AMOUNT)
    private lateinit var _capture: Capture

    companion object {
        private const val FRAME_AMOUNT: Int = 2
        private const val FRAME_LATENCY: Int = 2
        private const val FPS: Double = 30.00
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_camera)

        _capture = Capture(
            findViewById(R.id._cameraView),this,
            _base64ImgList, FRAME_AMOUNT, FRAME_LATENCY, FPS
        )

        findViewById<Button>(R.id._captureBtn).setOnClickListener {
            _capture.launchFramesCapture(0) {
                callbackOnImagesCompleted()
            }
            val i = 0
        }
    }

    private fun callbackOnImagesCompleted(): Unit {
        val callPAD: CallPAD = CallPAD(_base64ImgList[0], _base64ImgList[1])
        _base64ImgList.clear()
        //callPAD.sendPADRequest()
    }

    override fun onDestroy() {
        super.onDestroy()
    }
}