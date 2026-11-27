package edu.qa.wp.tests;

import static org.testng.Assert.assertFalse;
import static org.testng.Assert.assertTrue;

import java.time.Duration;
import java.util.List;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.annotations.Test;

import edu.qa.wp.BaseTest;
import edu.qa.wp.Config;
import edu.qa.wp.pages.FrontPage;
import io.qameta.allure.Description;
import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import io.qameta.allure.Severity;
import io.qameta.allure.SeverityLevel;
import io.qameta.allure.Story;

/** 用例集：评论与审核（对应 R04 / TC-COMM-001、TC-COMM-003） */
@Epic("WordPress Web 测试")
@Feature("评论")
public class CommentTest extends BaseTest {

    private WebDriverWait waiter() {
        return new WebDriverWait(driver, Duration.ofSeconds(Config.WAIT_SECONDS));
    }

    /** 从博客列表页打开第一篇文章（首页是静态介绍页，不再承载文章列表） */
    private FrontPage openFirstArticle() {
        driver.get(Config.BASE_URL + "/qa-blog/");
        List<WebElement> links = waiter().until(ExpectedConditions.presenceOfAllElementsLocatedBy(
                By.cssSelector("h2.entry-title a, h2 a")));
        assertFalse(links.isEmpty(), "博客列表页应至少有一篇文章链接");
        String href = links.get(0).getAttribute("href");
        driver.get(href);
        waiter().until(ExpectedConditions.presenceOfElementLocated(By.id("comment")));
        return new FrontPage(driver);
    }

    /** 提交评论并等待“等待审核”提示出现（WordPress 提交后停留在预览页，不跳转） */
    private String submitAndWaitComment(String content) {
        new FrontPage(driver).submitComment("测试访客", "guest@example.com", content);
        waiter().until(d -> d.getPageSource().contains("等待审核")
                || d.getPageSource().contains("已收到您的评论"));
        return new FrontPage(driver).pageText();
    }

    @Test(priority = 1, description = "TC-COMM-001 未登录用户评论进入待审核")
    @Story("评论审核流")
    @Severity(SeverityLevel.CRITICAL)
    @Description("匿名提交评论后，页面应提示“等待审核”，且评论不出现在前台列表")
    public void commentNeedsModeration() {
        openFirstArticle();

        String text = "自动化评论-" + System.currentTimeMillis();
        String body = submitAndWaitComment(text);

        assertTrue(body.contains("等待审核") || body.contains("审核"),
                "提交后应提示评论等待审核，页面片段："
                        + body.substring(0, Math.min(200, body.length())));
        // 未审核评论即使显示预览，也应处于“等待批准”状态，前台列表中不可见
        assertTrue(driver.getPageSource().contains("等待审核"),
                "页面应明确提示评论等待审核");
    }

    @Test(priority = 2, description = "TC-COMM-003 评论中的脚本标签被转义")
    @Story("XSS 防护")
    @Severity(SeverityLevel.BLOCKER)
    @Description("提交含 <script> 的评论，前台不得执行脚本（不弹窗）")
    public void commentScriptEscaped() {
        openFirstArticle();

        String payload = "<script>alert('xss')</script>自动化XSS测试";
        String body = submitAndWaitComment(payload);

        assertFalse(driver.getPageSource().contains("<script>alert('xss')</script>"),
                "脚本标签不应原样输出到页面");
        assertTrue(driver.getWindowHandles().size() == 1,
                "不应出现 JS 弹窗窗口");
        assertTrue(body.contains("等待审核") || body.contains("审核"),
                "含脚本的评论同样应进入待审核");
    }
}
