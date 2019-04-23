# IoTHubtoMonitor

Program.cs

A C# console app code for generating a Symmetric key to send a message to Azure IoT Hub. 

Heartbeat.cs

A Model for encapsulating the hearbeat

PostToLogAnalytics.py

Python Code to post to LogAnalytics. Will need to change to .NET


The high level arch is for the collectors to emit the telemetry to IoTHub, the messages from IoTHub will be routed to Event Hub to be consumed by anm Azure Function to post it to Log Analytics.

https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-event-grid-routing-comparison
