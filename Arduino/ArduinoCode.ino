    #include <RedBot.h>
    RedBotMotors motors;
    
    RedBotEncoder encoder = RedBotEncoder(A2, 10);
    RedBotSensor left = RedBotSensor(A3);   // initialize a left sensor object on A3
    RedBotSensor right = RedBotSensor(A7);   // initialize a right sensor object on A3
    RedBotSensor middle = RedBotSensor(A6);   // initialize a middle sensor object on A3
    
    int TRIG_PIN = A1;
    int ECHO_PIN = A0;
    
    int buttonPin = 12;
    int countsPerRev = 192;   // 4 pairs of N-S x 48:1 gearbox = 192 ticks per wheel rev
    
    float wheelDiam = 2.56;  // diam = 65mm / 25.4 mm/in
    float wheelCirc = PI*wheelDiam;  // Redbot wheel circumference = pi*D

    int regularMotorPower = 75;
    int emergencyMotorPower = 90;
    int motorPower = regularMotorPower;
    int EV = 10;
    int RV = 7;
    int bump = 10;
    long lineCounter = 0;
    //long lineRCounter = 0;
    //long lineLCounter = 0;
    int offsetGPSEV = 7;
    int offsetGPSRV = 7;

    int UltrasonicThreshold = 30;
    int UltrasonicOld = 100;
    bool reduceSpeed = false;

    
    void setup()
    {
      Serial.begin(115200);
      pinMode(TRIG_PIN, OUTPUT);
      pinMode(ECHO_PIN, INPUT);
      digitalWrite(TRIG_PIN, LOW);
    }
    
    void loop(void)
    {
      //driveStraight(12, 150); 
      // set the power for left & right motors on button press
      if (Serial.available() > 0)
      {
        char data = Serial.read();
        if(measureDistance()<bump){
          motors.brake();
        }
        else if (data == '1'){ // Send 1 to get Emergency vehicle
          motorPower = emergencyMotorPower;
          driveStraight(200, EV, offsetGPSEV);
        }
        else if (data == '2'){ // Send 2 to get regular vehicle
          motorPower = regularMotorPower;
          driveStraight(200, RV, offsetGPSRV);
        }
        else if (data == '3'){ // Send 3 to gps-server
          GPSServer();
        }
      }
    }
    
    void driveStraight(float distance, int offsetL, int offsetGPS)
    {
      int turnSpeed = 75;
      //float offsetL = (20-(offsetP * motorPower));
      char dataint;
      
      int LINETHRESHOLD = 980;
      
      long targetCount;
      float numRev;
    
      // variables for tracking the left and right encoder counts
      long prevlCount, prevrCount;
    
      long lDiff, rDiff;  // diff between current encoder count and previous count
    
      // variables for setting left and right motor power
      int leftPower = motorPower;
      int rightPower = motorPower;
    
      // variable used to offset motor power on right vs left to keep straight.
      int offset = 2;  // offset amount to compensate Right vs. Left drive
    
      numRev = distance / wheelCirc;  // calculate the target # of rotations
      targetCount = numRev * countsPerRev;    // calculate the target count

      long lCount = 0;
      long rCount = 0;
    
    
      encoder.clearEnc(BOTH);    // clear the encoder count
      //delay(100);  // short delay before starting the motors.
      
      motors.drive(motorPower);  // start motors
      //motors.leftDrive(motorPower + 50); 
    
      while (rCount < targetCount)
      {
        // while the right encoder is less than the target count -- debug print 
        // the encoder values and wait -- this is a holding loop.
        lCount = encoder.getTicks(LEFT);
        rCount = encoder.getTicks(RIGHT);
    
        motors.leftDrive(leftPower);
        motors.rightDrive(rightPower);
    
        // calculate the rotation "speed" as a difference in the count from previous cycle.
        lDiff = (lCount - prevlCount);
        rDiff = (rCount - prevrCount);
    
        // store the current count as the "previous" count for the next cycle.
        prevlCount = lCount;
        prevrCount = rCount;
    
        // if left is faster than the right, slow down the left / speed up right
        if (lDiff > rDiff) 
        {
          leftPower = leftPower - offset;
          rightPower = rightPower + offset;
        }
        // if right is faster than the left, speed up the left / slow down right
        else if (lDiff < rDiff) 
        {
          leftPower = leftPower + offset;  
          rightPower = rightPower - offset;
        }
        //delay(50);  // short delay to give motors a chance to respond.

       if (Serial.available() > 0){
        dataint = Serial.read();
       }
       if(dataint=='l'){
        leftPower = motorPower - offsetGPS;
        rightPower = motorPower + offsetGPS;
       }
       if(dataint=='r'){
        leftPower = motorPower + offsetGPS;
        rightPower = motorPower - offsetGPS;
       }
       if (dataint == '0'){
         motors.brake();
         break;
       }
       if (dataint == '1'){ // Send 1 to get Emergency vehicle
         motorPower = emergencyMotorPower;
         leftPower = motorPower;
         rightPower = motorPower;
         offsetL = EV;
       }
       if (dataint == '2'){ // Send 2 to get regular vehicle
         motorPower = regularMotorPower;
         leftPower = motorPower;
         rightPower = motorPower;
         offsetL = RV;
       }
       if (dataint == 'R'){
         motors.brake();
         delay(5);
         motors.leftDrive(turnSpeed);
         motors.rightDrive(-turnSpeed);
         while (true){
          if (Serial.available() > 0){
            char dataf = Serial.read();
            if (dataf == 'F'){
              motors.leftDrive(motorPower);
              motors.rightDrive(motorPower);
              break;
            }
          }
         }
       }
       if (dataint == 'L'){
         motors.brake();
         delay(5);
         motors.leftDrive(-turnSpeed);
         motors.rightDrive(turnSpeed);
         while (true){
          if (Serial.available() > 0){
            char dataf = Serial.read();
            if (dataf == 'F'){
              motors.leftDrive(motorPower);
              motors.rightDrive(motorPower);
              break;
            }
          }
         }
       }
       /*if(left.read() > LINETHRESHOLD && lineCounter > 40){ // && lineLCounter > 3
          leftPower = motorPower + offsetL;
          rightPower = motorPower - offsetL;
          //lineLCounter = 0;
        }
        if(right.read() > LINETHRESHOLD && lineCounter > 40){ //&& lineRCounter > 3
          leftPower = motorPower - offsetL;
          rightPower = motorPower + offsetL;
          //lineRCounter = 0;
        }      
        if(middle.read() > LINETHRESHOLD){
          motors.leftDrive(motorPower);
          motors.rightDrive(motorPower);
          lineCounter = 0;
          //delay(100-(motorPower*0.5));
        }
        lineCounter = lineCounter + 1;*/
        //lineRCounter = lineRCounter + 1;
        //lineLCounter = lineLCounter + 1;
        
        float ultraDistance = measureDistance();
        if(ultraDistance < bump){
          leftPower = 0;
          rightPower = 0;
          /*motors.brake();
          break;*/
        }
        if(ultraDistance < UltrasonicThreshold && ultraDistance < UltrasonicOld){ // if detect someting is slower in a distance of UltrasonicThreshold slows moters
          UltrasonicOld = ultraDistance;
          reduceSpeed = true;
          leftPower = leftPower-5;
          rightPower = rightPower-5;
        }
        if(ultraDistance > UltrasonicThreshold && reduceSpeed == true){ // if noting in front go back to original speed.
          reduceSpeed = false;
          leftPower = motorPower;
          rightPower = motorPower;
          UltrasonicOld = 100;
        }
     } 
    }
    void GPSServer(){
      while (true){
        if (Serial.available() > 0){
          String serie  = Serial.readStringUntil('\0');
          
            if(serie == "0"){
              motors.brake();
              break;
            }
            else{
              String lString = getValue(serie,';',0);
              String rString = getValue(serie,';',1);

              int rSpeed = rString.toInt();
              int lSpeed = lString.toInt();

              motors.leftDrive(lSpeed);
              motors.rightDrive(rSpeed);
           }
        }
      }
    }

    String getValue(String data, char separator, int index){
      int found = 0;
      int strIndex[] = {0, -1};
      int maxIndex = data.length()-1;

      for(int i=0; i<=maxIndex && found<=index; i++){
        if(data.charAt(i)==separator || i==maxIndex){
            found++;
            strIndex[0] = strIndex[1]+1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
      }

      return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
    }
    float measureDistance() {
      // uses HC-SR04 ultrasonic sensor
      unsigned long start_time, end_time, pulse_time;

      // trigger ultrasonic signal for 10 microseconds
      digitalWrite(TRIG_PIN, HIGH);
      delayMicroseconds(10);
      digitalWrite(TRIG_PIN, LOW);

      // wait until echo received
      while (digitalRead(ECHO_PIN) == 0);

      // measure how long echo lasts (pulse time)
      start_time = micros(); // get start time in microseconds
      while (digitalRead(ECHO_PIN) == 1); // wait until echo pulse ends
      end_time = micros(); // get end time
      pulse_time = end_time - start_time; // subtract to get duration

      // pulse time of 23200 represents maximum distance for this sensor
      if (pulse_time > 23200) pulse_time = 23200;

      // calculate distance to object using pulse time
      float dist_cm = pulse_time / 58.0;
      float dist_in = pulse_time / 148.0;

      // need 60 ms delay between ultrasonic sensor readings
      delay(60);

      // return distance value
      return dist_in*2.5; // or can return dist_cm
    }
