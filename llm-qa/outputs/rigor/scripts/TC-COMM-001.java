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

public class CommentSubmissionTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void submitCommentEntersPendingReview() {
        driver.get("https://example.com/article/1");

        WebElement commentBox = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("textarea[name='comment'], textarea#comment, textarea")));
        commentBox.clear();
        commentBox.sendKeys("自动化测试评论 " + System.currentTimeMillis());

        WebElement submitButton = wait.until(ExpectedConditions.elementToBeClickable(
                By.cssSelector("button[type='submit'], input[type='submit'], button.submit-comment")));
        submitButton.click();

        WebElement pendingMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.xpath("//*[contains(text(),'等待审核') or contains(text(),'待审核') or contains(text(),'审核中')]")));

        Assert.assertTrue(pendingMessage.isDisplayed(), "Expected pending review message to be displayed");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}