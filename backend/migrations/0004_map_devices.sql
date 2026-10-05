-- Update feedback_events to have a random device_id from ESP32-001 to ESP32-010
UPDATE feedback_events 
SET device_id = 'ESP32-' || substr('00' || ((ABS(RANDOM()) % 10) + 1), -3, 3)
WHERE device_id IS NULL;

-- Synchronize sensor_readings so it uses the same device_id as its parent event
UPDATE sensor_readings 
SET device_id = (SELECT device_id FROM feedback_events WHERE feedback_events.event_id = sensor_readings.event_id)
WHERE device_id IS NULL;
