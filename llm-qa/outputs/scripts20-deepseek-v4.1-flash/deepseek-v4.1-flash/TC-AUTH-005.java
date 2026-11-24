import org.openqa.selenium.By;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;
import java.util.List;

public class AuthLoginTest {

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        driver.get("https://example.com/login");
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void testCaptchaOrLockPromptAppearsAfterFiveWrongPasswordAttempts() {
        By usernameLocator = By.id("username");
        By passwordLocator = By.id("password");
        By loginButtonLocator = By.id("loginButton");
        By errorLocator = By.cssSelector(".error-message");
        By captchaLocator = By.cssSelector(".captcha, #captcha, [name='captcha']");
        By lockLocator = By.xpath("//*[contains(text(),'锁定') or contains(text(),'locked') or contains(text(),'Locked')]");

        for (int attempt = 1; attempt <= 5; attempt++) {
            WebElement username = wait.until(ExpectedConditions.visibilityOfElementLocated(usernameLocator));
            username.clear();
            username.sendKeys("testUser");

            WebElement password = wait.until(ExpectedConditions.visibilityOfElementLocated(passwordLocator));
            password.clear();
            password.sendKeys("WrongPassword" + attempt);

            wait.until(ExpectedConditions.elementToBeClickable(loginButtonLocator)).click();

            wait.until(d -> isAnyDisplayed(d, errorLocator, captchaLocator, lockLocator));
        }

        boolean promptDisplayed;
        try {
            promptDisplayed = wait.until(d -> isAnyDisplayed(d, captchaLocator, lockLocator));
        } catch (TimeoutException e) {
            promptDisplayed = false;
        }

        Assert.assertTrue(promptDisplayed, "Expected captcha or lock prompt after five consecutive wrong password attempts");
    }

    private boolean isAnyDisplayed(WebDriver driver, By... locators) {
        for (By locator : locators) {
            List<WebElement> elements = driver.findElements(locator);
            for (WebElement element : elements) {
                if (element.isDisplayed()) {
                    return true;
                }
            }
        }
        return false;
    }
}