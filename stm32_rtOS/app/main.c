#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"
#include <stdio.h>

QueueHandle_t sensorQueue;
SemaphoreHandle_t xMutex;

void vSensorTask(void *pvParameters) {
    for(;;) {
        int sample = 123; // example
        xQueueSend(sensorQueue, &sample, 0);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void vCommTask(void *pvParameters) {
    int val;
    for(;;) {
        if (xQueueReceive(sensorQueue, &val, portMAX_DELAY) == pdPASS) {
            // send via UART
        }
    }
}

int main(void) {
    sensorQueue = xQueueCreate(10, sizeof(int));
    xMutex = xSemaphoreCreateMutex();

    xTaskCreate(vSensorTask, "Sensor", 256, NULL, 2, NULL);
    xTaskCreate(vCommTask, "Comm", 256, NULL, 1, NULL);

    vTaskStartScheduler();
    for(;;);
}
