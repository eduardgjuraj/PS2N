#include <EEPROM.h>

int val;
int tempPin = A1; // Pin where the temperature sensor is connected
int pinLED = 5;

typedef struct EEPROMMessageEntry
{
    uint8_t valid;
    uint32_t timestamp;
    char message[EEPROM_MESSAGE_TABLE_MESSAGE_SIZE];
} EEPROMMessageEntry;

typedef struct EEPROMMessageTable
{
    EEPROMMessageEntry entry[EEPROM_MESSAGE_TABLE_ENTRIES_SIZE];
} EEPROMMessageTable;

static EEPROMMessageTable messageTable = {0};

static void readMessageTableFromEEPROM(void)
{
    EEPROM.get(EEPROM_MESSAGE_TABLE_START_ADDRESS, messageTable);
}

static void writeMessageTableToEEPROM(void)
{
    EEPROM.put(EEPROM_MESSAGE_TABLE_START_ADDRESS, messageTable);
}

static void addEntryToMessageTable(uint32_t timestamp, char *message)
{
    uint8_t entryIDMinTimestamp = 0;
    uint32_t minTimestamp = 0xFFFFFFFF;
    for(uint8_t entryID = 0; entryID < EEPROM_MESSAGE_TABLE_ENTRIES_SIZE; entryID++)
    {
        // Search for a free field
        if (0 == messageTable.entry[entryID].valid)
        {
            messageTable.entry[entryID].valid = 1;
            messageTable.entry[entryID].timestamp = timestamp;
            strcpy(messageTable.entry[entryID].message, message);

            // Field found
            return;
        }

        if (minTimestamp > messageTable.entry[entryID].timestamp)
        {
            entryIDMinTimestamp = entryID;
            minTimestamp = messageTable.entry[entryID].timestamp;
        }
    }

    // If there isn't any field that is free,
    // we will clear the oldest one and add the new one on it's slot
    messageTable.entry[entryIDMinTimestamp].valid = 1;
    messageTable.entry[entryIDMinTimestamp].timestamp = timestamp;
    strcpy(messageTable.entry[entryIDMinTimestamp].message, message);
}

static void serialCommandReadMessages(void)
{
    for(uint8_t message_nr = 0; message_nr < EEPROM_MESSAGE_TABLE_ENTRIES_SIZE; message_nr++)
    {
        // Make sure that each message has a string terminator
        messageTable.entry[message_nr].message[EEPROM_MESSAGE_TABLE_MESSAGE_SIZE - 1] = '\0';
        Serial.println(String(messageTable.entry[message_nr].valid) + "|" + 
                       String(messageTable.entry[message_nr].timestamp) + "|" + 
                       String(messageTable.entry[message_nr].message));
    }
}

static void serialCommandWriteMessage(void)
{
    char buffer[SERIAL_MESSAGE_BUFFER_SIZE];
    char *token;
    uint32_t timestamp;
    char message[EEPROM_MESSAGE_TABLE_MESSAGE_SIZE];

    int bufferLength = Serial.readBytesUntil('!', buffer, SERIAL_MESSAGE_BUFFER_SIZE);
    if(SERIAL_MESSAGE_BUFFER_SIZE == bufferLength)
    {
        bufferLength =  SERIAL_MESSAGE_BUFFER_SIZE - 1;
    }
    buffer[bufferLength] = '\0';
    
    token = strtok(buffer, "|");
    timestamp = atol(token);
    token = strtok(NULL, "|\n");
    memset(message, 0, sizeof(message));
    strncpy(message, token, EEPROM_MESSAGE_TABLE_MESSAGE_SIZE - 1);

    addEntryToMessageTable(timestamp, message);
    writeMessageTableToEEPROM();
}


void setup()
{
  Serial.begin(9600);
  // Set the LED pin as an output
  pinMode(pinLED, OUTPUT);
}

void loop()
{
  val = analogRead(tempPin);
  // Convert to Celsius
  float temperatura = (val * 5.0 * 100.0) / 1024.0;
  delay(1000);

  Serial.print(temperatura); // Include the actual temperature value
  Serial.println(); // Add a newline character
  
  if (Serial.available() > 0) {
    char command = Serial.read();

    // Check the received command and control the LED accordingly
    if (command == 'A') {
      digitalWrite(pinLED, HIGH);
    } else if (command == 'S') {
      digitalWrite(pinLED, LOW);
    }
  }

}

