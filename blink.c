#include <stdbool.h>
#include <stdint.h>

#define IO(a) ((volatile uint32_t*) (a))

#define DR_REG_SENS_BASE (0xC800)
#define SENS_SAR_PERI_CLK_GATE_CONF_REG IO(DR_REG_SENS_BASE + 0x0104)
#define SENS_IOMUX_CLK_EN (1 << 31)
#define DR_REG_RTC_IO_BASE (0xa400)
#define RTC_IO_TOUCH_PAD0_REG IO(DR_REG_RTC_IO_BASE + 0x0084)
#define RTC_IO_TOUCH_PAD0_MUX_SEL  (1 << 19)
#define RTC_GPIO_ENABLE_REG IO(DR_REG_RTC_IO_BASE + 0x0020)
#define RTC_GPIO_ENABLE_W1TS_REG IO(DR_REG_RTC_IO_BASE + 0x0024)
#define RTC_GPIO_OUT_W1TS_REG IO(DR_REG_RTC_IO_BASE + 0x0008)
#define RTC_GPIO_OUT_W1TC_REG IO(DR_REG_RTC_IO_BASE + 0x000C)

#define DR_REG_RTCCNTL_BASE (0x8000)
#define RTC_CNTL_COCPU_CTRL_REG IO(DR_REG_RTCCNTL_BASE + 0x0104)
#define RTC_CNTL_COCPU_DONE (1 << 25)
#define RTC_CNTL_COCPU_SHUT_RESET_EN (1 << 22)
#define RTC_CNTL_COCPU_SHUT_2_CLK_DIS_Pos (14)

#define ULP_RISCV_CYCLES_PER_MS 17500

// The pin number to blink
// a second line
uint32_t pin_number = 15;

// The delay between toggles
// a second line of comment
//
// A second paragraph
volatile uint32_t settingv1 = 0;

volatile uint32_t count = 1234;

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
    asm ("lui sp, 0x2000");
    // asm ("call rescue_from_monitor");
    asm ("call main");
    asm ("call shutdown");
}

int main (void) {
    count = 4321;
    bool gpio_level = true;

    // // ulp_riscv_gpio_init(GPIO_NUM_21);
    // *SENS_SAR_PERI_CLK_GATE_CONF_REG = SENS_IOMUX_CLK_EN;
    // *(RTC_IO_TOUCH_PAD0_REG + pin_number) = RTC_IO_TOUCH_PAD0_MUX_SEL;
    
    // // ulp_riscv_gpio_output_enable(GPIO_NUM_21);
    // *RTC_GPIO_ENABLE_W1TS_REG = 1 << pin_number;
    // count = (uint32_t) (SENS_SAR_PERI_CLK_GATE_CONF_REG);

    while (true) {
        count = 8762;
        // ulp_riscv_gpio_output_level(GPIO_NUM_21, gpio_level);
        // if (gpio_level) {
        //     *RTC_GPIO_OUT_W1TS_REG = 1 << pin_number;
        // } else {
        //     *RTC_GPIO_OUT_W1TC_REG = 1 << pin_number;
        // }
        // ulp_riscv_delay_cycles(shared_mem[0] * 10 * ULP_RISCV_CYCLES_PER_MS);
        uint32_t end;
        asm volatile("rdcycle %0;" : "=r"(end));
        uint32_t now = end;
        end += 10 * ULP_RISCV_CYCLES_PER_MS;
        while (now < end) {
            asm volatile("rdcycle %0;" : "=r"(now));
        }
        gpio_level = !gpio_level;
    }

    // ulp_riscv_shutdown() is called automatically when main exits
    return 0;
}
