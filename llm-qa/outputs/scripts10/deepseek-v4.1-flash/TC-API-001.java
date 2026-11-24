import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedCondition;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;

public class PostsAnonymousReadTest {

    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost");
    private static final String POSTS_ENDPOINT = BASE_URL + "/wp-json/wp/v2/posts";

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(20), Duration.ofMillis(500));
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void readPublishedPostsAnonymously() {
        driver.get(POSTS_ENDPOINT);

        String json = wait.until(new ExpectedCondition<String>() {
            @Override
            public String apply(WebDriver webDriver) {
                WebElement body = webDriver.findElement(By.tagName("body"));
                String text = body.getText() == null ? "" : body.getText().trim();
                return text.startsWith("[") && text.endsWith("]") ? text : null;
            }
        });

        Assert.assertNotNull(json, "Anonymous GET /wp-json/wp/v2/posts must return a JSON array of posts");
        Assert.assertTrue(json.length() > 2, "Posts collection should not be empty for a site with published posts");
        Assert.assertTrue(json.contains("\"status\":\"publish\""),
                "Every returned post must be published");
        Assert.assertFalse(json.contains("\"status\":\"draft\""),
                "Draft posts must not be exposed to anonymous users");
        Assert.assertFalse(json.contains("\"status\":\"pending\""),
                "Pending posts must not be exposed to anonymous users");
        Assert.assertFalse(json.contains("\"status\":\"private\""),
                "Private posts must not be exposed to anonymous users");
    }
}