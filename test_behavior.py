"""
Day 4 - Telemetry Simulation + Anomaly Detection Engine
With improvements: normalized baseline, anomaly reasons, timestamps
"""

import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.network_generator import NetworkGenerator
from src.core.telemetry_engine import TelemetryEngine
from src.core.anomaly_engine import AnomalyEngine


def main():
    print("=" * 80)
    print("📡 NetGraphIQ - Day 4: Behavioral Intelligence")
    print("=" * 80)
    print("\n🎯 Improvements:")
    print("   ✅ Normalized baseline display (rounded to 2 decimals)")
    print("   ✅ Anomaly reasons included")
    print("   ✅ Timestamps on all outputs")
    
    # Step 1: Generate network
    print("\n" + "=" * 80)
    print("🏗️  STEP 1: Network Topology")
    print("=" * 80)
    
    generator = NetworkGenerator()
    devices, connections = generator.generate_enterprise_network()
    
    print(f"\n   ✅ Network ready: {len(devices)} devices, {len(connections)} connections")
    
    # Step 2: Initialize telemetry engine
    print("\n" + "=" * 80)
    print("📊 STEP 2: Telemetry Engine Initialized")
    print("=" * 80)
    
    telemetry = TelemetryEngine(devices)
    print("   ✅ Ready to generate real-time traffic metrics")
    print("   📈 Normal variation: 70-130% of baseline (rounded to 2 decimals)")
    print("   ⚠️  Anomaly injection: 10% probability per device")
    
    # Step 3: Generate telemetry with anomalies
    print("\n" + "=" * 80)
    print("🎲 STEP 3: Generating Telemetry Data")
    print("=" * 80)
    
    current_metrics = telemetry.generate_telemetry(
        inject_anomalies=True,
        anomaly_rate=0.1
    )
    
    telemetry.print_telemetry_sample(limit=12)
    
    # Step 4: Detect anomalies
    print("\n" + "=" * 80)
    print("🔍 STEP 4: Anomaly Detection Engine")
    print("=" * 80)
    
    anomaly_engine = AnomalyEngine(devices)
    anomalies = anomaly_engine.detect_anomalies(current_metrics)
    
    # Step 5: Display anomalies
    anomaly_engine.print_anomalies(anomalies, limit=15)
    
    # Step 6: Statistical analysis
    print("\n" + "=" * 80)
    print("📈 STEP 5: Behavioral Analysis")
    print("=" * 80)
    
    if anomalies:
        # Show layer risk assessment
        risk_assessment = anomaly_engine.get_layer_risk_assessment(anomalies)
        print("\n   🎯 LAYER RISK ASSESSMENT:")
        for layer, risk in sorted(risk_assessment.items(), key=lambda x: x[1], reverse=True):
            if risk > 0:
                risk_bar = "█" * min(risk, 20)
                print(f"      {layer.upper():10} : {risk:3} points {risk_bar}")
        
        # Show statistical analysis for first anomaly
        first_anomaly = anomalies[0]
        print(f"\n   📊 STATISTICAL ANALYSIS - {first_anomaly['device_name']}:")
        stats = anomaly_engine.get_statistical_analysis(first_anomaly['device_id'])
        if 'error' not in stats:
            print(f"      Mean: {stats['mean']} pkts/sec")
            print(f"      Std Dev: {stats['std_dev']} pkts/sec")
            print(f"      Stable: {'✅ Yes' if stats['is_stable'] else '⚠️ No'}")
    
    # Step 7: Summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    
    summary = anomaly_engine.get_anomaly_summary()
    
    print(f"\n   Total Anomalies Detected: {summary['total_anomalies']}")
    
    if summary['total_anomalies'] > 0:
        print("\n   By Severity:")
        for severity, count in summary['by_severity'].items():
            icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}.get(severity, '⚪')
            print(f"      {icon} {severity.upper()}: {count}")
        
        print("\n   By Layer:")
        for layer, count in summary['by_layer'].items():
            print(f"      📍 {layer.upper()}: {count}")
        
        print("\n   By Type:")
        for atype, count in summary['by_type'].items():
            print(f"      🔥 {atype.replace('_', ' ').title()}: {count}")
    
    # Success metrics
    print("\n" + "=" * 80)
    print("✅ DAY 4 COMPLETE - Behavioral Intelligence Achieved")
    print("=" * 80)
    
    print("\n🎯 WHAT WE ACCOMPLISHED:")
    print("   1. ✅ Real-time telemetry simulation")
    print("   2. ✅ Normalized baseline display (rounded values)")
    print("   3. ✅ Anomaly reasons with root cause analysis")
    print("   4. ✅ Timestamp tracking on all events")
    print("   5. ✅ Severity classification (LOW → CRITICAL)")
    print("   6. ✅ Layer-aware anomaly tracking")
    print("   7. ✅ Actionable recommendations")
    
    print("\n💡 KEY INSIGHTS:")
    print(f"   • {len(devices)} devices monitored")
    print(f"   • {len(anomalies)} behavioral anomalies detected")
    print(f"   • {len([a for a in anomalies if a['severity'] == 'critical'])} critical events requiring immediate action")
    
    return devices, telemetry, anomaly_engine, anomalies


if __name__ == "__main__":
    print("\n🚀 Starting NetGraphIQ Behavioral Monitoring System...\n")
    random.seed(42)  # Set seed for reproducibility
    devices, telemetry, anomaly_engine, anomalies = main()
    print("\n✨ Behavioral monitoring session complete!")