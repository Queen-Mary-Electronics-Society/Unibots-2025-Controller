// Obstacle Avoidance with curved paths

//Pin definitions for Ultrasonic obstacle sensor
const int pingPin = A0;
const int echoPin = A1;

//Pin definitions for avoid sensor
const int left_sensor = A5;
const int right_sensor = A4;

const int SPEED = 80;
long duration;
float distance;
float distance_prev;
long duration_current;
long reverseSpeed;
long FWDSpeed;



//Pin definitions for Left motor
int enable_motor_left=5;
int In_left_a=7;
int In_left_b=6;

//Pin definitions for Right motor
int enable_motor_right=10;
int In_right_a=9;
int In_right_b=8;

void setup() 
{

  pinMode(right_sensor, INPUT);// initiate Right avoidance sensor
  pinMode(left_sensor, INPUT);// initiate Left avoidance sensor

 // Serial.begin(9600);  
}

void loop() 
{
  distance = distance_cm(); //calling the distance calculation subroutine

 // ------ If avoid infra-red sensors are active - hard reverse -----
  if (analogRead(left_sensor) < 200 || analogRead(right_sensor) < 200)
  {                              
    reverseSpeed = SPEED;
    right_motor_backward(reverseSpeed * random(1,1.5));
    left_motor_backward(reverseSpeed * random(1,1.5)); 
    delay (random(500,850));
 //   Serial.print(reverseSpeed);
//    Serial.println(" HIGH reverse Speed - avoid sensors activated");     
  }

 //--------- If ultrasound sensor distance is away from obstacle as shown --------
  else if (distance > 35)
  {                              
    FWDSpeed = min (SPEED, distance * 1.8); // reducing speed from 80 to 67.5, the closer we get.                                  
    right_motor_forward(FWDSpeed);
    left_motor_forward(FWDSpeed); 
 //   Serial.print(FWDSpeed);
 //   Serial.println(" FWDSPeed - distance > 50");       
  }
  
  //------- If distance is within shown interval and approaching obstacle -------
//  else if ((distance > 35 && distance < 45) && (distance_prev - distance > 3))
  // robot slows down from 67.5 to 52.5
//  {                              
//    FWDSpeed = distance * 1.5;                                   
//    right_motor_forward(FWDSpeed);
//    left_motor_forward(FWDSpeed); 
 //   Serial.print(FWDSpeed);
 //   Serial.println(" FWDSPeed - distance between 35 and 55");       
 // }

  // ----- If robot has stopped in front of obstacle - make a backward move ----
  else if ((distance <= 35) && (distance_prev - distance == 0))  // ((distance_prev - distance < 2) || (distance - distance_prev < 2)))
  {                              
    reverseSpeed = SPEED; // * 3;
    right_motor_backward(reverseSpeed);
    left_motor_forward(reverseSpeed); 
    delay(300);
 //   Serial.print(reverseSpeed);
 //   Serial.println(" reverse Speed - distance < 51; motor stop");     
  }
 
  distance_prev = distance;
}

void right_motor_forward(int pwm)
{
  analogWrite(enable_motor_right,pwm);  // Switching the enabling pin of left motor high
  digitalWrite(In_right_a,HIGH);            // setting one directional pin of motor to high
  digitalWrite(In_right_b,LOW);
}


void right_motor_backward(int pwm)
{
  analogWrite(enable_motor_right,pwm);  // Switching the enabling pin of left motor high
  digitalWrite(In_right_a,LOW);            // setting one directional pin of motor to high
  digitalWrite(In_right_b,HIGH);
}


void left_motor_forward(int pwm)
{
  analogWrite(enable_motor_left,pwm);  // Switching the enabling pin of left motor high
  digitalWrite(In_left_a,HIGH);             // setting one directional pin of motor to high
  digitalWrite(In_left_b,LOW);            // setting other pin of left motor to low
}


void left_motor_backward(int pwm)
{
  analogWrite(enable_motor_left,pwm);  // Switching the enabling pin of left motor high
  digitalWrite(In_left_a,LOW);             // setting one directional pin of motor to high
  digitalWrite(In_left_b,HIGH);            // setting other pin of left motor to low
}

long duration_rout()      //Sub-routine to calculate distance from the obstacle
{
  digitalWrite(pingPin, LOW);
  delayMicroseconds(2);
  digitalWrite(pingPin, HIGH);
  delayMicroseconds(5);
  digitalWrite(pingPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  return duration;
}

float distance_cm() //Sub-routine to convert calculated distance to cm
{
  // The speed of sound is 340 m/s or 29 microseconds per centimeter.
  // The ping travels out and back, so to find the distance of the object we
  // take half of the distance travelled.
  duration_current = duration_rout();
  return duration_current / 2.9 / 20;
}
