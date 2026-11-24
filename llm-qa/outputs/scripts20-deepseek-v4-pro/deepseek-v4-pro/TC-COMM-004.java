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

public class AdminReplyCommentTest {

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void testAdminReplyCommentShowsNestedReplyOnFrontEnd() {
        // Open admin comment list
        driver.get("http://example.com/admin/comments");
        
        WebElement replyButton = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(".comment-item:first-child .reply-btn")));
        replyButton.click();
        
        WebElement replyTextArea = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("reply-text")));
        replyTextArea.sendKeys("This is a nested reply from admin.");
        
        WebElement submitReplyBtn = driver.findElement(By.id("submit-reply"));
        submitReplyBtn.click();
        
        wait.until(ExpectedConditions.invisibilityOfElementLocated(By.id("reply-text")));
        
        // Go to front end article page
        driver.get("http://example.com/article/1");
        
        WebElement nestedReply = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".comment-nested .reply-content")));
        
        String actualReplyText = nestedReply.getText();
        Assert.assertTrue(actualReplyText.contains("This is a nested reply from admin."),
                "The nested reply should be displayed on the front end.");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}