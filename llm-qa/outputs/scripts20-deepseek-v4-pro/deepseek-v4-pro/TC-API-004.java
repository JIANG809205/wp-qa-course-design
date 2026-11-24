import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;

public class ApiPaginationTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void testPaginationBoundaryPerPageExceedsLimitReturns400() {
        driver.get("http://example.com/api/items?per_page=101");
        wait.until(ExpectedConditions.titleContains("400"));
        String pageSource = driver.getPageSource();
        Assert.assertTrue(pageSource.contains("参数错误"),
                "Response should contain '参数错误' error message");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}