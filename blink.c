#include <stdbool.h>
#include <stdint.h>

#define IO(a) ((volatile uint32_t*) (a))

#define DR_REG_SENS_BASE (0xC800)
#define S3_SENS_SAR_PERI_CLK_GATE_CONF_REG IO(DR_REG_SENS_BASE + 0x0104)
#define S3_SENS_IOMUX_CLK_EN (1 << 31)
#define S2_SENS_SAR_IO_MUX_CONF_REG IO(DR_REG_SENS_BASE + 0x0144)
#define S2_SENS_IOMUX_CLK_GATE_EN (1 << 31)
#define DR_REG_RTC_IO_BASE (0xa400)
#define RTC_IO_TOUCH_PAD0_REG IO(DR_REG_RTC_IO_BASE + 0x0084)
#define RTC_IO_TOUCH_PAD0_MUX_SEL  (1 << 19)
#define RTC_GPIO_ENABLE_REG IO(DR_REG_RTC_IO_BASE + 0x000C)
#define RTC_GPIO_ENABLE_W1TS_REG IO(DR_REG_RTC_IO_BASE + 0x0010)
#define RTC_GPIO_OUT_W1TS_REG IO(DR_REG_RTC_IO_BASE + 0x0004)
#define RTC_GPIO_OUT_W1TC_REG IO(DR_REG_RTC_IO_BASE + 0x0008)

#define DR_REG_RTCCNTL_BASE (0x8000)
#define RTC_CNTL_COCPU_CTRL_REG IO(DR_REG_RTCCNTL_BASE + 0x0104)
#define RTC_CNTL_COCPU_DONE (1 << 25)
#define RTC_CNTL_COCPU_SHUT_RESET_EN (1 << 22)
#define RTC_CNTL_COCPU_SHUT_2_CLK_DIS_Pos (14)

#define ULP_RISCV_CYCLES_PER_MS 17500

typedef uint32_t cp_mcu_pin_number_t;

// The pin to blink
cp_mcu_pin_number_t led_pin = 15;

// Sx chip version
uint32_t sx_version = 3;

// The delay between toggles in milliseconds
volatile uint32_t delay = 500;

void __attribute__((naked)) reset(void) {
    asm ("j start");
}

void __attribute__((naked)) interrupt(void) {
    asm ("ret");
}


static void __attribute__((used)) rescue_from_monitor(void) {
    *RTC_CNTL_COCPU_CTRL_REG &= ~(RTC_CNTL_COCPU_DONE | RTC_CNTL_COCPU_SHUT_RESET_EN);
} 

static void __attribute__((used)) shutdown(void) {
    /* Setting the delay time after RISCV recv `DONE` signal, Ensure that action `RESET` can be executed in time. */
    *RTC_CNTL_COCPU_CTRL_REG = 0x3f << RTC_CNTL_COCPU_SHUT_2_CLK_DIS_Pos;

    /* suspends the ulp operation*/
    *RTC_CNTL_COCPU_CTRL_REG |= RTC_CNTL_COCPU_DONE;

    /* Resets the processor */
    *RTC_CNTL_COCPU_CTRL_REG |= RTC_CNTL_COCPU_SHUT_RESET_EN;
}

void __attribute__((naked)) start(void) {
    asm ("lui sp, 0x2");
    asm ("call rescue_from_monitor");
    asm ("call main");
    asm ("call shutdown");
}

int main (void) {
    bool gpio_level = true;
    uint32_t cycles_per_ms = 0;
    // // ulp_riscv_gpio_init(GPIO_NUM_21);
    if (sx_version == 3) {
        *S3_SENS_SAR_PERI_CLK_GATE_CONF_REG = S3_SENS_IOMUX_CLK_EN;
        cycles_per_ms = 17500;
    } else if (sx_version == 2) {
        *S2_SENS_SAR_IO_MUX_CONF_REG = S2_SENS_IOMUX_CLK_GATE_EN;
        cycles_per_ms = 8500;
    }
    *(RTC_IO_TOUCH_PAD0_REG + led_pin) = RTC_IO_TOUCH_PAD0_MUX_SEL;
    
    // // ulp_riscv_gpio_output_enable(GPIO_NUM_21);
    *RTC_GPIO_ENABLE_W1TS_REG = 1 << (led_pin + 10);

    while (true) {
        // ulp_riscv_gpio_output_level(GPIO_NUM_21, gpio_level);
        if (gpio_level) {
            *RTC_GPIO_OUT_W1TS_REG = 1 << (led_pin + 10);
        } else {
            *RTC_GPIO_OUT_W1TC_REG = 1 << (led_pin + 10);
        }
        // ulp_riscv_delay_cycles(shared_mem[0] * 10 * ULP_RISCV_CYCLES_PER_MS);
        uint32_t end;
        asm volatile("rdcycle %0;" : "=r"(end));
        uint32_t now = end;
        end += delay * cycles_per_ms;
        while (now < end) {
            asm volatile("rdcycle %0;" : "=r"(now));
        }
        gpio_level = !gpio_level;
    }

    // ulp_riscv_shutdown() is called automatically when main exits
    return 0;
}
