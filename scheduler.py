import schedule
import time
import json
import logging
from datetime import datetime
from main import main as run_email_assistant

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_schedule_time():
    """从配置文件加载定时时间"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('schedule_time', '09:00')
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        return '09:00'


def job():
    """定时任务"""
    logger.info("定时任务触发，开始执行邮件助手...")
    try:
        run_email_assistant()
    except Exception as e:
        logger.error(f"执行邮件助手时发生错误: {str(e)}", exc_info=True)


def main():
    """主函数 - 运行定时任务"""
    schedule_time = load_schedule_time()
    
    logger.info("=" * 60)
    logger.info("邮件助手定时任务已启动")
    logger.info(f"每天 {schedule_time} 自动运行")
    logger.info("按 Ctrl+C 停止")
    logger.info("=" * 60)
    
    # 设置定时任务
    schedule.every().day.at(schedule_time).do(job)
    
    # 可选：立即执行一次
    logger.info("是否立即执行一次？等待5秒...（按Ctrl+C取消）")
    try:
        time.sleep(5)
        logger.info("立即执行一次...")
        job()
    except KeyboardInterrupt:
        logger.info("已取消立即执行")
    
    # 持续运行
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("\n定时任务已停止")
            break
        except Exception as e:
            logger.error(f"定时任务发生错误: {str(e)}", exc_info=True)
            time.sleep(60)


if __name__ == "__main__":
    main()

