package fr.ensicaen.eng.ntnu.mobai.framescapturer

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL


class CallPAD(base64StringEncodedFrame_one: String, base64StringEncodedFrame_two: String) {
    private val _base64StringEncodedFrame_one = base64StringEncodedFrame_one
    private val _base64StringEncodedFrame_two = base64StringEncodedFrame_two

    public fun sendPADRequest()
    {
        val url = URL("http://10.0.2.15:8080/ListOfImageToDecode")
        val httpURLConnection = url.openConnection() as HttpURLConnection
        //prepare input data
        val jsonObject = JSONObject()
        val listOfFrames = listOf(_base64StringEncodedFrame_one, _base64StringEncodedFrame_two)
        val tempJsonString = JSONArray(listOfFrames)
        jsonObject.put("listStr64_image", tempJsonString)
        val jsonObjectString = jsonObject.toString()

        GlobalScope.launch(Dispatchers.IO) {
            httpURLConnection.requestMethod = "POST"
            httpURLConnection.setRequestProperty("Content-Type", "application/json") // The format of the content we're sending to the server
            httpURLConnection.setRequestProperty("Accept", "application/json") // The format of response we want to get from the server
            httpURLConnection.setRequestProperty("Ocp-Apim-Subscription-Key", "***********************")
            httpURLConnection.doInput = true
            httpURLConnection.doOutput = true
            // Send the JSON we created
            val outputStreamWriter = OutputStreamWriter(httpURLConnection.outputStream)
            outputStreamWriter.write(jsonObjectString)
            outputStreamWriter.flush()
            // Check if the connection is successful
            val responseCode = httpURLConnection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = httpURLConnection.inputStream.bufferedReader()
                    .use { it.readText() }
                withContext(Dispatchers.Main) {
                    val json = JSONObject(response)
                    val bPAD_decision = json.get("decision") as Boolean
                    val strScore = json.get("score").toString()
                }
            } else {
                Log.e("HTTPURLCONNECTION_ERROR", responseCode.toString())
            }
        }
    }
}