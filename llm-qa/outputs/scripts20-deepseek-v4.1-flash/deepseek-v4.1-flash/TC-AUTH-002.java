import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;
import java.time.Duration;

public class AuthLoginTest {
    @Test
    public void loginWithIncorrectPasswordShouldShowError() {
        WebDriver driver = new ChromeDriver();
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        try {
            driver.get("https://example.com/login");

            WebElement username = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username")));
            username.clear();
            username.sendKeys("validUser");

            WebElement password = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("password")));
            password.clear();
            password.sendKeys("wrongPassword");

            wait.until(ExpectedConditions.elementToBeClickable(By.id("loginButton"))).click();

            WebElement errorMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".error-message")));
            Assert.assertTrue(errorMessage.getText().contains("密码不正确"),
                    "Expected error message to contain '密码不正确', but was: " + errorMessage.getText());
        } finally {
            driver.quit();
        }
    }
}