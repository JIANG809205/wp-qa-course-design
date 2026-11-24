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

public class ArticleDraftTest {

    private static final String BASE_URL = "http://localhost:8080";
    private static final Duration TIMEOUT = Duration.ofSeconds(15);

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, TIMEOUT);
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void saveArticleDraft() {
        driver.get(BASE_URL + "/articles/new");

        WebElement titleInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("article-title")));
        titleInput.clear();
        titleInput.sendKeys("Selenium 自动化草稿");

        WebElement saveDraftButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.id("save-draft-button")));
        saveDraftButton.click();

        WebElement toast = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".toast-message")));

        Assert.assertEquals(toast.getText().trim(), "草稿已更新", "保存草稿后的提示信息不符合预期");
    }
}