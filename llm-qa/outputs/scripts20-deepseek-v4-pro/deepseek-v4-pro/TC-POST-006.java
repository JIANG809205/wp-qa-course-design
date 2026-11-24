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
import io.github.bonigarcia.wdm.WebDriverManager;

import java.time.Duration;

public class PostTrashRestoreTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        driver = new ChromeDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        driver.manage().window().maximize();
    }

    @Test
    public void testMovePostToTrashAndRestore() {
        // Open post list
        driver.get("https://example.com/admin/posts");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("posts-table")));

        WebElement firstPostRow = driver.findElement(By.cssSelector("#posts-table tbody tr:first-child"));
        String postTitle = firstPostRow.findElement(By.cssSelector(".post-title")).getText();
        WebElement moveToTrashLink = firstPostRow.findElement(By.linkText("移至回收站"));
        
        // Move to trash
        moveToTrashLink.click();
        try {
            wait.until(ExpectedConditions.alertIsPresent());
            driver.switchTo().alert().accept();
        } catch (Exception ignored) {}
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".notice-success")));

        // Navigate to trash
        driver.get("https://example.com/admin/posts/trash");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("trash-table")));
        
        // Restore the post
        WebElement trashRow = driver.findElement(By.xpath("//table[@id='trash-table']//td[contains(text(),'" + postTitle + "')]/.."));
        WebElement restoreLink = trashRow.findElement(By.linkText("还原"));
        restoreLink.click();
        try {
            wait.until(ExpectedConditions.alertIsPresent());
            driver.switchTo().alert().accept();
        } catch (Exception ignored) {}
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".notice-success")));

        // Verify restored post status
        driver.get("https://example.com/admin/posts");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("posts-table")));
        
        WebElement restoredPostRow = driver.findElement(By.xpath("//table[@id='posts-table']//td[contains(text(),'" + postTitle + "')]/.."));
        String status = restoredPostRow.findElement(By.cssSelector(".post-status")).getText();
        Assert.assertEquals(status, "已发布", "Post should be restored to 已发布 status");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}