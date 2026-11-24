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
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class PostSchedulingTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
    }

    @Test
    public void schedulePostForFuturePublish() {
        driver.get("https://example.com/admin/posts/new");

        // 设置未来时间：明天此时
        LocalDateTime tomorrow = LocalDateTime.now().plusDays(1);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm");
        String futureTime = tomorrow.format(formatter);
        WebElement timeInput = driver.findElement(By.id("schedule-time"));
        timeInput.sendKeys(futureTime);

        // 保存
        driver.findElement(By.id("save-btn")).click();

        // 等待状态更新为“已安排”
        WebElement statusLabel = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".post-status")));
        String actualStatus = statusLabel.getText();
        Assert.assertEquals(actualStatus, "已安排", "期望文章状态为已安排");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}