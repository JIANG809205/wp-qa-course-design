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

public class AdminCommentReplyTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void adminRepliesToCommentAndFrontendShowsNestedReply() {
        String adminCommentsUrl = System.getProperty("admin.comments.url", "http://localhost:8080/admin/comments");
        String frontendCommentsUrl = System.getProperty("frontend.comments.url", "http://localhost:8080/comments");
        String replyText = "Thanks for your comment.";

        driver.get(adminCommentsUrl);

        WebElement commentList = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='admin-comment-list']")));
        Assert.assertTrue(commentList.isDisplayed(), "Admin comment list should be visible");

        WebElement replyButton = wait.until(ExpectedConditions.elementToBeClickable(
                By.cssSelector("[data-testid='admin-comment-list'] [data-testid='comment-item']:first-child [data-testid='reply-button']")));
        replyButton.click();

        WebElement replyInput = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='reply-form'] textarea[name='reply']")));
        replyInput.clear();
        replyInput.sendKeys(replyText);

        WebElement submitButton = wait.until(ExpectedConditions.elementToBeClickable(
                By.cssSelector("[data-testid='reply-form'] button[type='submit']")));
        submitButton.click();

        WebElement successMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='toast-success']")));
        Assert.assertTrue(successMessage.isDisplayed(), "Reply submission should show success message");

        driver.get(frontendCommentsUrl);

        WebElement nestedReply = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='comment-list'] [data-testid='comment-item'] [data-testid='comment-children'] [data-testid='comment-reply']")));
        Assert.assertEquals(nestedReply.getText().trim(), replyText, "Frontend should display the nested reply");
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}