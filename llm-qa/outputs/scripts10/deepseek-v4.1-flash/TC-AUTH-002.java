package tests;

import java.time.Duration;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class LoginTest {

    private static final String BASE_URL = "https://example.com/login";
    private static final Duration TIMEOUT = Duration.ofSeconds(15);

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, TIMEOUT);
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void loginWithWrongPasswordShouldShowError() {
        driver.get(BASE_URL);

        WebElement usernameInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("username")));
        usernameInput.clear();
        usernameInput.sendKeys("validUser");

        WebElement passwordInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("password")));
        passwordInput.clear();
        passwordInput.sendKeys("wrongPassword123");

        WebElement submitButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']")));
        submitButton.click();

        WebElement errorMessage = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".error-message, [role='alert']")));

        Assert.assertEquals(errorMessage.getText().trim(), "密码不正确", "错误提示信息不符合预期");
        Assert.assertTrue(errorMessage.isDisplayed(), "错误提示应可见");
    }
}