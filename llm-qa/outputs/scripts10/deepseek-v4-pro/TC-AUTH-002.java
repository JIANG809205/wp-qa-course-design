import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;
import java.time.Duration;

public class LoginTest {
    WebDriver driver; // assume initialized

    @Test
    public void testLoginWithIncorrectPassword() {
        driver.get("https://example.com/login");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username")));
        usernameField.sendKeys("correctUsername");
        WebElement passwordField = driver.findElement(By.id("password"));
        passwordField.sendKeys("wrongPassword");
        driver.findElement(By.id("loginButton")).click();
        WebElement errorMsg = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("error")));
        Assert.assertEquals(errorMsg.getText(), "密码不正确");
    }
}