import java.time.Duration;

import org.json.JSONArray;
import org.json.JSONObject;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

public class PostsAnonymousReadTest {

    private static final String BASE_URL = "https://your-site-under-test.com";
    private static final Duration TIMEOUT = Duration.ofSeconds(20);
    private static final String POSTS_ENDPOINT = "/wp-json/wp/v2/posts";

    private WebDriver driver;

    @Test
    public void readPostsListAsAnonymousUser() {
        WebDriverWait wait = new WebDriverWait(driver, TIMEOUT);

        driver.get(BASE_URL + POSTS_ENDPOINT);

        WebElement body = wait.until(ExpectedConditions.presenceOfElementLocated(By.tagName("body")));

        wait.until(d -> {
            String text = d.findElement(By.tagName("body")).getText().trim();
            return text.startsWith("[") || text.startsWith("{");
        });

        String rawJson = driver.findElement(By.tagName("body")).getText().trim();

        Assert.assertTrue(rawJson.startsWith("["), "Anonymous posts request should return a JSON array, but got: " + rawJson);

        JSONArray posts = new JSONArray(rawJson);

        Assert.assertTrue(posts.length() > 0, "Anonymous request should return at least one published post");

        for (int i = 0; i < posts.length(); i++) {
            JSONObject post = posts.getJSONObject(i);
            Assert.assertEquals(post.optString("status"), "publish",
                    "Post with id " + post.optInt("id") + " should not be returned because it is not published");
        }
    }
}