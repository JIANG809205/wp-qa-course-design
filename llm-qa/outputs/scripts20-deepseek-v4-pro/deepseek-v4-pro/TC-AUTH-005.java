import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;

import static org.testng.Assert.assertTrue;

public class AuthTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(5));
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        driver.get("https://example.com/login"); // 实际URL请替换
    }

    @Test
    public void testConsecutiveFailedLoginShowsCaptchaOrLockoutMessage() {
        for (int i = 0; i < 5; i++) {
            driver.findElement(By.id("username")).sendKeys("testuser");
            driver.findElement(By.id("password")).sendKeys("wrongpassword");
            driver.findElement(By.id("loginButton")).click();
            sleep(1000); // 等待页面反应
        }

        try {
            wait.until(ExpectedConditions.or(
                    ExpectedConditions.visibilityOfElementLocated(By.id("captcha")),
                    ExpectedConditions.visibilityOfElementLocated(By.id("lockMessage"))
            ));
        } catch (Exception e) {
            throw new AssertionError("验证码或锁定提示未在规定时间内出现", e);
        }

        boolean captchaVisible = !driver.findElements(By.id("captcha")).isEmpty() && driver.findElement(By.id("captcha")).isDisplayed();
        boolean lockVisible = !driver.findElements(By.id("lockMessage")).isEmpty() && driver.findElement(By.id("lockMessage")).isDisplayed();
        assertTrue(captchaVisible || lockVisible, "预期出现验证码或锁定提示，但两者均未显示");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    private void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}