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

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void saveArticleDraft() {
        driver.get("http://localhost:8080/editor");

        wait.until(ExpectedConditions.elementToBeClickable(By.linkText("新建文章"))).click();

        WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("input[placeholder*='标题'], input[name='title']")));
        titleInput.clear();
        titleInput.sendKeys("Test Article Draft");

        wait.until(ExpectedConditions.elementToBeClickable(
                By.xpath("//button[contains(normalize-space(.),'保存草稿')]"))).click();

        WebElement toast = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.xpath("//*[contains(normalize-space(.),'草稿已更新')]")));

        Assert.assertTrue(toast.isDisplayed(), "Draft updated message should be displayed");
        Assert.assertEquals(toast.getText().trim(), "草稿已更新");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}