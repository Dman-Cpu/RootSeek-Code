import UIKit
import CoreML
import Foundation

class MyDataViewController: UIViewController {
    @IBOutlet weak var temperatureLabel: UILabel!
    @IBOutlet weak var humidityLabel: UILabel!
    @IBOutlet weak var distanceLabel: UILabel!
    @IBOutlet weak var rootDetectionLabel: UILabel!
    
    let model = "tree_root_model" // CoreML model
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Initialize UI labels
        temperatureLabel.text = "Temperature: --"
        humidityLabel.text = "Humidity: --"
        distanceLabel.text = "Distance: --"
        rootDetectionLabel.text = "Root Detection: --"
        
        //URL of ESP32 server
        let url = "http://192.168.7.218/data"
        
        // Fetch data from ESP32
        fetchAndParseData(from: url)
    }
    
    // Fetch and parse data from ESP32
    func fetchAndParseData(from url: String) {
        guard let url = URL(string: url) else {
            print("Invalid URL.")
            return
        }
        
        // Perform the HTTP request
        URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
            if let error = error {
                print("Error fetching data: \(error.localizedDescription)")
                return
            }
            
            guard let data = data else {
                print("No data received.")
                return
            }
            
            // Attempt to decode the JSON into a SensorData object
            do {
                // Parse the JSON data manually
                guard let jsonData = String(data: data, encoding: .utf8),
                      let parsedData = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                      let temp = parsedData["temperature"] as? Double,
                      let hum = parsedData["humidity"] as? Double,
                      let dist = parsedData["distance"] as? Double else {
                    print("Error parsing JSON data.")
                    return
                }
                
                // Update UI with sensor data
                DispatchQueue.main.async {
                    self?.updateSensorData(temperature: temp, humidity: hum, distance: dist)
                }
                
                // Process prediction
                //self?.processPrediction(temperature: temp, humidity: hum, distance: dist)
                
            } catch {
                print("Error decoding JSON data: \(error)")
            }
        }.resume()
    }
    
    // Update the sensor data UI
    func updateSensorData(temperature: Double, humidity: Double, distance: Double) {
        temperatureLabel.text = "Temperature: \(temperature) °C"
        humidityLabel.text = "Humidity: \(humidity) %"
        distanceLabel.text = "Distance: \(distance) cm"
    }
    
    // Process prediction using CoreML model
    func processPrediction(temperature: Double, humidity: Double, distance: Double) {
        do {
            // Create the model input
            let input = tree_root_modelInput(distance: distance, temperature: temperature, humidity: humidity)
            let prediction = try model.prediction(input: input)
            
            // Use the correct field from the model output
            let rootDetected = prediction.label == 1  // Adjust this based on your model's output
            
            // Update UI based on prediction
            rootDetectionLabel.text = rootDetected ? "Roots Detected!" : "No Roots Detected"
            
            if rootDetected {
                triggerAlert("Roots Detected!", "Please check the tree roots.")
            }
        } catch {
            print("Prediction error: \(error)")
        }
    }
    
    // Trigger an alert
    func triggerAlert(_ title: String, _ message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default, handler: nil))
        self.present(alert, animated: true, completion: nil)
    }
}

