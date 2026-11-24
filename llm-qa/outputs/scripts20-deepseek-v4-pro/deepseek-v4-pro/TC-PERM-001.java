import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;
import java.time.Duration;
import java.util.List;

public class ArticlePermissionTest {
    WebDriver driver;
    WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        driver.manage().window().maximize();
    }

    @Test
    public void testContributorHasNoPublishButton() {
        driver.get("https://example.com/login");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username"))).sendKeys("contributor_user");
        driver.findElement(By.id("password")).sendKeys("password");
        driver.findElement(By.id("loginButton")).click();

        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user-avatar")));

        driver.get("https://example.com/article/new");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("article-editor")));

        List<WebElement> publishButtons = driver.findElements(By.xpath("//button[contains(text(),'发布')]"));
        assert publishButtons.isEmpty() : "发布按钮不应该存在";

        WebElement submitReviewButton = wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//button[contains(text(),'提交复审')]")));
        assert submitReviewButton.isDisplayed() : "提交复审按钮应该显示";
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}