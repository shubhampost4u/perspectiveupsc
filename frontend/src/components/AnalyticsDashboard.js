import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#EC4899'];

const AnalyticsDashboard = ({ token }) => {
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [revenueChart, setRevenueChart] = useState(null);
  const [userGrowth, setUserGrowth] = useState(null);
  const [topTests, setTopTests] = useState([]);
  const [bundleBreakdown, setBundleBreakdown] = useState(null);
  const [testPerformance, setTestPerformance] = useState([]);
  const [recentPurchases, setRecentPurchases] = useState([]);
  const [timeFilter, setTimeFilter] = useState('30'); // days
  const [chartPeriod, setChartPeriod] = useState('daily');

  useEffect(() => {
    fetchAnalytics();
  }, [timeFilter, chartPeriod]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const config = { headers: { Authorization: `Bearer ${token}` } };

      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - parseInt(timeFilter));

      // Fetch all analytics data
      const [
        overviewRes,
        revenueChartRes,
        userGrowthRes,
        topTestsRes,
        bundleRes,
        performanceRes,
        recentRes
      ] = await Promise.all([
        axios.get(`${API}/admin/analytics/overview?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`, config),
        axios.get(`${API}/admin/analytics/revenue-chart?period=${chartPeriod}&days=${timeFilter}`, config),
        axios.get(`${API}/admin/analytics/user-growth?days=${timeFilter}`, config),
        axios.get(`${API}/admin/analytics/top-tests?limit=10`, config),
        axios.get(`${API}/admin/analytics/bundle-breakdown`, config),
        axios.get(`${API}/admin/analytics/test-performance`, config),
        axios.get(`${API}/admin/analytics/recent-purchases?limit=10`, config)
      ]);

      setOverview(overviewRes.data);
      setRevenueChart(revenueChartRes.data);
      setUserGrowth(userGrowthRes.data);
      setTopTests(topTestsRes.data);
      setBundleBreakdown(bundleRes.data);
      setTestPerformance(performanceRes.data);
      setRecentPurchases(recentRes.data);
    } catch (error) {
      console.error('Analytics fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">Comprehensive sales, revenue, and growth metrics</p>
        </div>
        
        {/* Time Filter */}
        <div className="flex gap-2">
          <select
            value={timeFilter}
            onChange={(e) => setTimeFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="7">Last 7 Days</option>
            <option value="30">Last 30 Days</option>
            <option value="90">Last 90 Days</option>
            <option value="365">Last Year</option>
          </select>
          
          <select
            value={chartPeriod}
            onChange={(e) => setChartPeriod(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Revenue */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Revenue</CardDescription>
            <CardTitle className="text-3xl">₹{overview?.revenue?.total?.toLocaleString()}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-600">
              Period: ₹{overview?.revenue?.period?.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        {/* Today's Revenue */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Today's Revenue</CardDescription>
            <CardTitle className="text-3xl text-green-600">₹{overview?.revenue?.today?.toLocaleString()}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-600">
              This Month: ₹{overview?.revenue?.this_month?.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        {/* Total Students */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Students</CardDescription>
            <CardTitle className="text-3xl text-blue-600">{overview?.students?.total?.toLocaleString()}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-600">
              Active (30d): {overview?.students?.active_30d}
            </div>
          </CardContent>
        </Card>

        {/* Total Orders */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Orders</CardDescription>
            <CardTitle className="text-3xl text-purple-600">{overview?.orders?.total?.toLocaleString()}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-600">
              Avg: ₹{overview?.revenue?.average_order_value?.toFixed(2)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Revenue Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Revenue Trend</CardTitle>
          <CardDescription>Revenue and orders over time</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueChart?.labels?.map((label, idx) => ({
              date: label,
              revenue: revenueChart.revenue[idx],
              orders: revenueChart.orders[idx]
            })) || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="revenue" stroke="#3B82F6" name="Revenue (₹)" strokeWidth={2} />
              <Line yAxisId="right" type="monotone" dataKey="orders" stroke="#8B5CF6" name="Orders" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* User Growth Chart */}
      <Card>
        <CardHeader>
          <CardTitle>User Growth</CardTitle>
          <CardDescription>New student registrations</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={userGrowth?.labels?.map((label, idx) => ({
              date: label,
              registrations: userGrowth.registrations[idx]
            })) || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="registrations" fill="#10B981" name="New Registrations" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Top Tests and Bundle Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Selling Tests */}
        <Card>
          <CardHeader>
            <CardTitle>Top Selling Tests</CardTitle>
            <CardDescription>Best performing tests by revenue</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topTests.slice(0, 5).map((test, idx) => (
                <div key={test.test_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                      {idx + 1}
                    </div>
                    <div>
                      <div className="font-medium">{test.test_name}</div>
                      <div className="text-sm text-gray-600">{test.sales} sales</div>
                    </div>
                  </div>
                  <div className="text-lg font-bold text-green-600">
                    ₹{test.revenue.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Bundle Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Bundle Sales Breakdown</CardTitle>
            <CardDescription>Revenue by bundle size</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={Object.entries(bundleBreakdown || {}).map(([key, value]) => ({
                    name: key.replace('_', ' ').replace('tests', 'Tests'),
                    value: value.revenue,
                    count: value.count
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ₹${value.toLocaleString()}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {Object.keys(bundleBreakdown || {}).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {Object.entries(bundleBreakdown || {}).map(([key, value], idx) => (
                <div key={key} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded" style={{ backgroundColor: COLORS[idx] }}></div>
                    <span>{key.replace('_', ' ')}</span>
                  </div>
                  <span className="font-medium">{value.count} orders ({value.discount_percent}% off)</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Test Performance Table */}
      <Card>
        <CardHeader>
          <CardTitle>Test Performance</CardTitle>
          <CardDescription>Attempts, scores, and completion rates</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3 font-semibold">Test Name</th>
                  <th className="text-right p-3 font-semibold">Attempts</th>
                  <th className="text-right p-3 font-semibold">Avg Score</th>
                  <th className="text-right p-3 font-semibold">Completion Rate</th>
                </tr>
              </thead>
              <tbody>
                {testPerformance.slice(0, 10).map((test) => (
                  <tr key={test.test_id} className="border-b hover:bg-gray-50">
                    <td className="p-3">{test.test_name}</td>
                    <td className="p-3 text-right">{test.attempts}</td>
                    <td className="p-3 text-right font-medium">{test.avg_score}%</td>
                    <td className="p-3 text-right">
                      <span className={`px-2 py-1 rounded ${
                        test.completion_rate > 80 ? 'bg-green-100 text-green-700' :
                        test.completion_rate > 50 ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {test.completion_rate}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Recent Purchases */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Purchases</CardTitle>
          <CardDescription>Latest transaction history</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3 font-semibold">Student</th>
                  <th className="text-left p-3 font-semibold">Test</th>
                  <th className="text-right p-3 font-semibold">Amount</th>
                  <th className="text-left p-3 font-semibold">Payment ID</th>
                  <th className="text-left p-3 font-semibold">Date</th>
                </tr>
              </thead>
              <tbody>
                {recentPurchases.map((purchase) => (
                  <tr key={purchase.purchase_id} className="border-b hover:bg-gray-50">
                    <td className="p-3">
                      <div className="font-medium">{purchase.student_name}</div>
                      <div className="text-sm text-gray-600">{purchase.student_email}</div>
                    </td>
                    <td className="p-3">{purchase.test_name}</td>
                    <td className="p-3 text-right font-bold text-green-600">₹{purchase.amount}</td>
                    <td className="p-3 text-xs text-gray-600">{purchase.payment_id}</td>
                    <td className="p-3 text-sm">{new Date(purchase.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Active Users</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Last 7 days</span>
              <span className="font-bold">{overview?.students?.active_7d}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Last 30 days</span>
              <span className="font-bold">{overview?.students?.active_30d}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">New in period</span>
              <span className="font-bold text-green-600">+{overview?.students?.new_in_period}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Test Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Tests</span>
              <span className="font-bold">{overview?.tests?.total}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Total Attempts</span>
              <span className="font-bold">{overview?.tests?.total_attempts}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Period Attempts</span>
              <span className="font-bold text-blue-600">{overview?.tests?.period_attempts}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Orders Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Orders</span>
              <span className="font-bold">{overview?.orders?.total}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Period Orders</span>
              <span className="font-bold">{overview?.orders?.period}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Avg Order Value</span>
              <span className="font-bold text-purple-600">₹{overview?.revenue?.average_order_value?.toFixed(2)}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center">
        <Button onClick={fetchAnalytics} className="bg-blue-600 hover:bg-blue-700">
          Refresh Analytics
        </Button>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
