package edu.qa.wp;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.testng.ITestListener;
import org.testng.ITestResult;

import io.qameta.allure.Allure;

/** 失败自动截图，并附带页面 URL 与标题，方便定位 */
public class TestListener implements ITestListener {

    private static final DateTimeFormatter TS = DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss");

    @Override
    public void onTestFailure(ITestResult result) {
        Object driverObj = result.getTestContext().getAttribute("driver");
        if (!(driverObj instanceof WebDriver driver)) {
            return;
        }
        try {
            byte[] png = ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);

            Path dir = Paths.get("target", "screenshots");
            Files.createDirectories(dir);
            String name = result.getName() + "-" + LocalDateTime.now().format(TS) + ".png";
            Files.write(dir.resolve(name), png);

            Allure.addAttachment("失败截图 " + result.getName(),
                    "image/png", new ByteArrayInputStream(png), ".png");
            Allure.addAttachment("失败页面信息", "text/plain",
                    "URL: " + driver.getCurrentUrl() + System.lineSeparator()
                            + "TITLE: " + driver.getTitle(),
                    ".txt");

            System.out.println("[FAIL-SHOT] " + new File(dir.toFile(), name).getAbsolutePath());
        } catch (Exception e) {
            System.err.println("[FAIL-SHOT] 截图失败: " + e.getMessage());
        }
    }
}
