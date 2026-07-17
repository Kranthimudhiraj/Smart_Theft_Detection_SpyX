#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

int netWeight = 1;   // net weight in Kg

void setup() {
  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Net Weight:");
  lcd.setCursor(0, 1);
  lcd.print(netWeight);
  lcd.print(" Kg");
}

void loop() {}
