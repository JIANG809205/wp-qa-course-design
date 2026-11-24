import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.time.Duration;

public class UserPermissionTest {

    private WebDriver driver;
    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost:8080");
    private static final Duration TIMEOUT = Duration.ofSeconds(15);

    @Test
    public void editUserCannotAccessCreateUserPage() {
        WebDriverWait wait = new WebDriverWait(driver, TIMEOUT);

        driver.get(BASE_URL + "/login");
        WebElement usernameInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username")));
        usernameInput.clear();
        usernameInput.sendKeys("editor");
        WebElement passwordInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("password")));
        passwordInput.clear();
        passwordInput.sendKeys("editor123");
        wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']"))).click();
        WebElement userInfo = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user-info")));
        Assert.assertTrue(userInfo.isDisplayed(), "编辑身份登录失败");

        driver.get(BASE_URL + "/users/create");

        WebElement deniedMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector(".access-denied, .error-message, [data-testid='access-denied']")));

        Assert.assertTrue(deniedMessage.isDisplayed(), "编辑身份访问新建用户页应显示拒绝访问提示");
        Assert.assertTrue(!driver.getCurrentUrl().endsWith("/users/create")
                        || deniedMessage.getText().toLowerCase().contains("denied")
                        || deniedMessage.getText().contains("拒绝")
                        || deniedMessage.getText().contains("无权限"),
                "编辑身份不应被允许访问新建用户页");
    }
}