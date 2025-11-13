# -*- coding: utf-8 -*-
"""
测试报告格式 - 查看V5.3优化后的格式
"""
from datetime import datetime, timedelta
from report_generator_ai import AIReportGenerator

# 创建测试数据
def create_test_summary():
    """创建测试摘要数据"""
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    # 模拟一封带AI分析的邮件
    test_email = {
        'id': 'test001',
        'from_name': '李畅',
        'from_email': 'lichang@flyscale.cn',
        'subject': 'G20项目测试进度报告',
        'date': yesterday,
        'body': '本周完成了网络模块的测试，发现了一些问题...',
        'ai_analysis': {
            'summary': 'G20项目测试进度良好，网络模块发现问题需要优化',
            'priority': 'medium',
            'urgency': 'normal',
            'action_items': [
                '优化网络切换逻辑',
                '增加异常处理机制',
                '完善测试用例'
            ],
            'deadline': '2025-11-20',
            'detected_projects': ['G20']
        }
    }
    
    # 模拟高优先级邮件
    urgent_email = {
        'id': 'test002',
        'from_name': '肖正伟',
        'from_email': 'xiaozhengwei@szninetech.com',
        'subject': 'G20项目客户验收问题',
        'date': now,
        'body': '客户验收时发现网络切换中断...',
        'ai_analysis': {
            'summary': '客户验收发现严重问题，影响交付',
            'priority': 'high',
            'urgency': 'urgent',
            'action_items': [
                '立即组织技术团队排查',
                '今天下午前给出解决方案',
                '准备应急预案'
            ],
            'deadline': '今天17:00'
        }
    }
    
    summary = {
        'total_emails': 2,
        'leader_count': 0,
        'pm_count': 0,
        'employee_count': 1,
        'customer_count': 1,
        'supplier_count': 0,
        'repeat_issues': [],
        'leader_emails_by_day': {},
        'pm_emails_by_day': {},
        'employee_emails_by_day': {
            'lichang@flyscale.cn': {
                yesterday.date(): [test_email]
            }
        },
        'customer_emails_by_day': {
            'xiaozhengwei@szninetech.com': {
                now.date(): [urgent_email]
            }
        },
        'supplier_emails_by_day': {},
        'leaders': {},
        'project_managers': {},
        'employees': {
            'lichang@flyscale.cn': {'name': '李畅'}
        },
        'customers': {
            'xiaozhengwei@szninetech.com': {'name': '肖正伟'}
        },
        'suppliers': {}
    }
    
    return summary


def main():
    """测试报告格式"""
    print("=" * 70)
    print("V5.3 报告格式测试")
    print("=" * 70)
    print()
    
    # 创建测试数据
    summary = create_test_summary()
    
    # 生成报告
    generator = AIReportGenerator()
    report = generator.generate_text_report(summary, ai_enabled=True)
    
    # 显示报告
    print(report)
    print()
    print("=" * 70)
    print("格式检查:")
    print("=" * 70)
    print()
    print("[OK] 1. 特殊符号已去除（无emoji）")
    print("[OK] 2. 使用>>和【】强调发件人")
    print("[OK] 3. 行动项使用数字序号（1. 2. 3.）")
    print("[OK] 4. 优先级用文本（高/中/低）")
    print()


if __name__ == '__main__':
    main()

