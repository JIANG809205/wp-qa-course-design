import java.time.Duration;

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

public class ArticleDraftTest {

    private static final String BASE_URL = "http://localhost:8080";
    private static final Duration TIMEOUT = Duration.ofSeconds(15);

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, TIMEOUT);
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test(description = "TC-POST-001: save article draft and verify the toast message")
    public void saveArticleDraft() {
        driver.get(BASE_URL + "/article/new");

        WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("input#article-title, input[name='title'], textarea[placeholder*='标题']")));
        titleInput.clear();
        titleInput.sendKeys("Test Article Draft " + System.currentTimeMillis());

        WebElement saveDraftButton = wait.until(ExpectedConditions.elementToBeClickable(
                By.xpath("//button[contains(normalize-space(.), '保存草稿')]")));
        saveDraftButton.click();

        WebElement toast = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector(".toast, .toast-message, .el-message, .ant-message-notice-content")));

        String actualMessage = toast.getText().trim();
        Assert.assertTrue(actualMessage.contains("草稿已更新"),
                "Expected toast to contain '草稿已更新' but was: " + actualMessage);
    }
}