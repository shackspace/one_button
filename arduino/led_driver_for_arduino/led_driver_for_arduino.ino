#include "FastLED.h"

// How many leds in your strip?
#define NUM_LEDS 4

// For led chips like Neopixels, which have a data line, ground, and power, you just
// need to define DATA_PIN.  For led chipsets that are SPI based (four wires - data, clock,
// ground, and power), like the LPD8806 define both DATA_PIN and CLOCK_PIN
#define DATA_PIN 2
#define CLOCK_PIN 13

// Define the array of leds
CRGB leds[NUM_LEDS];
  void turn_color(int r,int g,int b){
    	for(int i = 0; i < NUM_LEDS; i++) {
		// Set the i'th led to red 
		leds[i].r = r;
		leds[i].g = g;
		leds[i].b = b;

		// Show the leds
		// now that we've shown the leds, reset the i'th led to black
		// Wait a little bit before we loop around and do it again
	}
        FastLED.show();

  }
void setup() { 
      // Uncomment/edit one of the following lines for your leds arrangement.
      // FastLED.addLeds<TM1803, DATA_PIN, RGB>(leds, NUM_LEDS);
      // FastLED.addLeds<TM1804, DATA_PIN, RGB>(leds, NUM_LEDS);
      // FastLED.addLeds<TM1809, DATA_PIN, RGB>(leds, NUM_LEDS);
// FastLED.addLeds<WS2811, DATA_PIN, RGB>(leds, NUM_LEDS);
FastLED.addLeds<WS2812, DATA_PIN, RGB>(leds, NUM_LEDS);
      // FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds, NUM_LEDS);
  //	  FastLED.addLeds<NEOPIXEL, DATA_PIN, RGB>(leds, NUM_LEDS);
      // FastLED.addLeds<UCS1903, DATA_PIN, RGB>(leds, NUM_LEDS);

      // FastLED.addLeds<WS2801, RGB>(leds, NUM_LEDS);
      // FastLED.addLeds<SM16716, RGB>(leds, NUM_LEDS);
      // FastLED.addLeds<LPD8806, RGB>(leds, NUM_LEDS);

      // FastLED.addLeds<WS2801, DATA_PIN, CLOCK_PIN, RGB>(leds, NUM_LEDS);
      // FastLED.addLeds<SM16716, DATA_PIN, CLOCK_PIN, RGB>(leds, NUM_LEDS);
      // FastLED.addLeds<LPD8806, DATA_PIN, CLOCK_PIN, RGB>(leds, NUM_LEDS);
         Serial.begin(9600);
         Serial.println("Balls");
    
  turn_color(0,255,0);

}

void loop() { 
     while (Serial.available() > 0) {
            int r = Serial.parseInt();
            int g = Serial.parseInt();
            int b = Serial.parseInt();

                 if (Serial.read() == '\n') {
                               turn_color(r,g,b);
                                //Serial.print(r, HEX);
                                //                                Serial.print(g, HEX);

                                //Serial.println(b, HEX);

                 }
     }
  /*
  // Turn the LED on, then pause
  leds[0] = CRGB::Red;
    leds[1] = CRGB::Red;
  leds[2] = CRGB::Red;
  leds[3] = CRGB::Red;

  FastLED.show();
  delay(5000);
  // Now turn the LED off, then pause
  leds[0] = CRGB::Black;
    leds[1] = CRGB::Black;
  leds[2] = CRGB::Black;
  leds[3] = CRGB::Black;

  FastLED.show();
  delay(5000);
  */
}
