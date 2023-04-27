package fr.ensicaen.eng.ntnu.mobai.injectionattackanalysis

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setupCameraButton()
    }

    private fun setupCameraButton() {
        val btn = findViewById<Button>(R.id._camera)
        btn.setOnClickListener {
            val intent = Intent(this, FramesCapture::class.java)
            startActivity(intent)
        }
    }
}