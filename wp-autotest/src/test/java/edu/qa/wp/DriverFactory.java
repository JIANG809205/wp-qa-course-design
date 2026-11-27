package edu.qa.wp;

import java.time.Duration;

import org.openqa.selenium.PageLoadStrategy;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

/** 浏览器工厂：统一 headless 配置，便于在服务器/WSL 中运行 */
public final class DriverFactory {

    private DriverFactory() {
    }

    public static WebDriver create() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments(
                "--headless=new",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-background-networking",
                "--no-first-run",
                "--window-size=1440,900",
                "--lang=zh-CN");
        options.setAcceptInsecureCerts(true);
        // eager：DOMContentLoaded 即返回，避免评论提交后渲染器迟迟不结束加载导致 30 秒超时
        options.setPageLoadStrategy(PageLoadStrategy.EAGER);

        WebDriver driver = new ChromeDriver(options);
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(60));
        driver.manage().timeouts().implicitlyWait(Duration.ZERO);
        return driver;
    }
}
