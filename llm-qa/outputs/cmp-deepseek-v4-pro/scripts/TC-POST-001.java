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

public class ArticleTest {

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        driver.get("https://example.com/admin/articles/new"); // 假设的URL
    }

    @Test
    public void testSaveArticleDraft() {
        // 步骤1: 进入新建文章 (已在setUp中进入)

        // 步骤2: 填写标题
        WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("article-title")));
        titleInput.clear();
        titleInput.sendKeys("测试文章标题");

        // 步骤3: 点击保存草稿
        WebElement saveDraftBtn = driver.findElement(By.id("save-draft-btn"));
        wait.until(ExpectedConditions.elementToBeClickable(saveDraftBtn)).click();

        // 预期结果：提示草稿已更新
        WebElement toastMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".toast-success")));
        String actualMessage = toastMessage.getText();
        Assert.assertEquals(actualMessage, "草稿已更新", "草稿保存成功提示信息不正确");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}