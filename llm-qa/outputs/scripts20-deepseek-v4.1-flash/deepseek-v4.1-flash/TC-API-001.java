import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;
import java.util.List;

public class PostApiTest {

    private WebDriver driver;
    private WebDriverWait wait;

    private static final String BASE_URL =
            System.getProperty("baseUrl", "https://wordpress.example.com");

    @BeforeMethod
    public void setUp() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new");
        options.addArguments("--disable-gpu");
        driver = new ChromeDriver(options);
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
    }

    @Test
    public void readAnonymousPostListReturnsOnlyPublishedPosts() {
        driver.get(BASE_URL + "/wp-json/wp/v2/posts");

        wait.until(ExpectedConditions.presenceOfElementLocated(By.tagName("body")));

        String jsonText = wait.until(d -> {
            String text = (String) ((JavascriptExecutor) d)
                    .executeScript("return document.body.innerText;");
            return (text != null && text.trim().startsWith("[")) ? text.trim() : null;
        });

        @SuppressWarnings("unchecked")
        List<String> statuses = (List<String>) ((JavascriptExecutor) driver).executeScript(
                "return JSON.parse(arguments[0]).map(function(post){return post.status;});",
                jsonText);

        Assert.assertNotNull(statuses, "Response should be a JSON array of posts");
        Assert.assertFalse(statuses.isEmpty(), "Anonymous post list should not be empty");
        for (String status : statuses) {
            Assert.assertEquals(status, "publish",
                    "Anonymous post list must only contain published posts");
        }
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}