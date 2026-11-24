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

public class CommentTest {
    private WebDriver driver;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
    }

    @Test
    public void submitCommentAndVerifyPendingReview() {
        driver.get("https://example.com/article");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        WebElement commentField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("comment-input")));
        commentField.sendKeys("这是一条测试评论");
        driver.findElement(By.id("submit-btn")).click();
        WebElement message = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("submission-message")));
        Assert.assertEquals(message.getText(), "您的评论已提交，等待审核。");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}