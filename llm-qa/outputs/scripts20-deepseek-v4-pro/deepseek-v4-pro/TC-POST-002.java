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

public class PostPublishTest {

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void testPublishDraft() {
        // 打开草稿页面（假设为该用例预先准备好的草稿详情/编辑页）
        driver.get("http://example.com/drafts/123/edit");

        // 等待发布按钮可点击并点击
        WebElement publishButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.id("publish-button")));
        publishButton.click();

        // 等待状态元素可见并获取其文本
        WebElement statusLabel = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("post-status")));
        String actualStatus = statusLabel.getText();

        // 断言状态变为 “已发布”
        Assert.assertEquals(actualStatus, "已发布", "状态未更新为已发布");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}