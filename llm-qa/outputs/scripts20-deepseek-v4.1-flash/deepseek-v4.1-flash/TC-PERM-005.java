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

import java.time.Duration;
import java.util.List;

public class ArticlePermissionTest {

    private static final String BASE_URL = "http://localhost:8080";
    private static final String OTHER_AUTHOR_ARTICLE_ID = "1002";

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void authorCannotDeleteOthersArticle() {
        loginAsAuthor("author01", "Password123!");

        driver.get(BASE_URL + "/articles/" + OTHER_AUTHOR_ARTICLE_ID);
        WebElement articleTitle = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[data-testid='article-title']")));
        Assert.assertTrue(articleTitle.isDisplayed(), "Article page of another author should be viewable");

        List<WebElement> deleteButtons = driver.findElements(
                By.cssSelector("[data-testid='article-delete-button'], button.delete-article"));

        if (deleteButtons.isEmpty()) {
            Assert.assertTrue(articleTitle.isDisplayed(),
                    "No delete entry should be rendered for an article owned by another author");
        } else {
            deleteButtons.get(0).click();

            List<WebElement> confirmButtons = driver.findElements(
                    By.cssSelector("[data-testid='confirm-delete'], .modal-confirm-delete"));
            if (!confirmButtons.isEmpty()) {
                confirmButtons.get(0).click();
            }

            WebElement errorMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(
                    By.cssSelector("[data-testid='toast-error'], .error-message, .alert-danger")));
            String message = errorMessage.getText().trim().toLowerCase();
            Assert.assertTrue(
                    message.contains("denied") || message.contains("forbidden")
                            || message.contains("permission") || message.contains("无权限")
                            || message.contains("拒绝"),
                    "Deleting another author's article must be rejected, actual message: " + message);
            Assert.assertTrue(articleTitle.isDisplayed(),
                    "Article should still exist after a rejected delete operation");
        }

        driver.get(BASE_URL + "/articles/" + OTHER_AUTHOR_ARTICLE_ID + "/delete");
        WebElement forbidden = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='error-page'], .error-page, .alert-danger")));
        Assert.assertTrue(forbidden.isDisplayed(),
                "Direct delete request on another author's article must be rejected");
    }

    private void loginAsAuthor(String username, String password) {
        driver.get(BASE_URL + "/login");
        WebElement usernameInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[data-testid='username'], input[name='username']")));
        usernameInput.clear();
        usernameInput.sendKeys(username);

        WebElement passwordInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[data-testid='password'], input[name='password']")));
        passwordInput.clear();
        passwordInput.sendKeys(password);

        WebElement submitButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.cssSelector("[data-testid='login-submit'], button[type='submit']")));
        submitButton.click();

        wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='user-menu'], .user-avatar")));
    }
}