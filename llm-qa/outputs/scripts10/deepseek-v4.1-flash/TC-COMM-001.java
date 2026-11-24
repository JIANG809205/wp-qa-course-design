import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.time.Duration;

public class CommentSubmissionTest {

    private static final By ARTICLE_LINK = By.cssSelector("article h2 a, .post-title a");
    private static final By COMMENT_INPUT = By.cssSelector("textarea#comment, textarea[name='comment']");
    private static final By SUBMIT_BUTTON = By.cssSelector("button[type='submit'], input[type='submit'], button.comment-submit");
    private static final By PENDING_NOTICE = By.xpath(
            "//*[contains(normalize-space(text()),'等待审核') or contains(normalize-space(text()),'待审核')]");

    @Test
    public void submitCommentGoesToPendingReview() {
        WebDriver driver = new ChromeDriver();
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        try {
            driver.manage().window().maximize();
            driver.get("https://example.com/");

            WebElement articleLink = wait.until(ExpectedConditions.elementToBeClickable(ARTICLE_LINK));
            articleLink.click();

            WebElement commentBox = wait.until(ExpectedConditions.visibilityOfElementLocated(COMMENT_INPUT));
            commentBox.clear();
            commentBox.sendKeys("Automated test comment " + System.currentTimeMillis());

            WebElement submitButton = wait.until(ExpectedConditions.elementToBeClickable(SUBMIT_BUTTON));
            submitButton.click();

            WebElement notice = wait.until(ExpectedConditions.visibilityOfElementLocated(PENDING_NOTICE));
            String noticeText = notice.getText().trim();

            Assert.assertTrue(noticeText.contains("等待审核") || noticeText.contains("待审核"),
                    "Expected a pending-review notice but got: " + noticeText);
        } finally {
            driver.quit();
        }
    }
}