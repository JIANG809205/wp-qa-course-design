import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterClass;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

import java.time.Duration;
import java.util.List;
import java.util.Map;

public class ArticleApiTest {
    private WebDriver driver;
    private final String BASE_URL = "http://your-wordpress-site.com"; // 替换为实际站点

    @BeforeClass
    public void setUp() {
        System.setProperty("webdriver.chrome.driver", "path/to/chromedriver");
        driver = new ChromeDriver();
        driver.get(BASE_URL);
    }

    @Test
    public void testAnonymousReadPostsReturnsOnlyPublishedArticles() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        wait.until(webDriver -> ((JavascriptExecutor) webDriver)
                .executeScript("return document.readyState").equals("complete"));

        String asyncScript = 
            "var callback = arguments[arguments.length - 1];" +
            "fetch('/wp-json/wp/v2/posts')" +
            "  .then(response => response.json())" +
            "  .then(data => callback(data))" +
            "  .catch(error => callback(null));";

        Object response = ((JavascriptExecutor) driver).executeAsyncScript(asyncScript);
        Assert.assertNotNull(response, "API should return data");

        Assert.assertTrue(response instanceof List, "Response should be a JSON array");
        List<Map<String, Object>> posts = (List<Map<String, Object>>) response;

        for (Map<String, Object> post : posts) {
            String status = (String) post.get("status");
            Assert.assertEquals(status, "publish", "All posts must be published");
        }
    }

    @AfterClass
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}