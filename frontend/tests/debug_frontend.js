/**
 * 前端API联合调试脚本
 * 用于测试前后端API匹配情况
 */

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';
const API_KEY = process.env.API_KEY || 'test-api-key';

async function debugRequest(method, endpoint, data = null, token = null) {
  const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const options = { method, headers };
  
  if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
    options.body = JSON.stringify(data);
  }
  
  console.log(`\n${'='.repeat(60)}`);
  console.log(`${method} ${endpoint}`);
  if (data) console.log('Request:', JSON.stringify(data, null, 2));
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const contentType = response.headers.get('content-type');
    let result;
    
    if (contentType && contentType.includes('application/json')) {
      result = await response.json();
    } else {
      result = await response.text();
    }
    
    console.log(`Status: ${response.status} ${response.statusText}`);
    console.log('Response:', typeof result === 'string' ? result : JSON.stringify(result, null, 2));
    
    return { success: response.ok, status: response.status, data: result };
  } catch (error) {
    console.error('Error:', error.message);
    return { success: false, error: error.message };
  }
}

async function runConsumerAppTests() {
  console.log('\n' + '★'.repeat(30));
  console.log('消费者端应用测试');
  console.log('★'.repeat(30));
  
  const tests = [
    {
      name: '发送聊天消息',
      method: 'POST',
      endpoint: '/api/v1/chat/sessions',
      data: { message: '你好，我想咨询产品问题', sessionId: null }
    },
    {
      name: '获取知识库列表',
      method: 'GET',
      endpoint: '/api/v1/knowledge'
    },
    {
      name: '获取知识库详情',
      method: 'GET',
      endpoint: '/api/v1/knowledge/1'
    },
    {
      name: '搜索知识库',
      method: 'POST',
      endpoint: '/api/v1/knowledge/search',
      data: { query: '产品', topK: 5 }
    }
  ];
  
  for (const test of tests) {
    await debugRequest(test.method, test.endpoint, test.data);
  }
}

async function runEnterpriseAppTests() {
  console.log('\n' + '★'.repeat(30));
  console.log('企业管理端应用测试');
  console.log('★'.repeat(30));
  
  const tests = [
    {
      name: '企业管理员登录',
      method: 'POST',
      endpoint: '/api/v1/auth/login',
      data: { email: 'admin@company.com', password: 'password123' }
    },
    {
      name: '获取企业信息',
      method: 'GET',
      endpoint: '/api/v1/enterprise/profile'
    },
    {
      name: '获取会话列表',
      method: 'GET',
      endpoint: '/api/v1/chat/sessions'
    },
    {
      name: '获取会话详情',
      method: 'GET',
      endpoint: '/api/v1/chat/sessions/1'
    },
    {
      name: '获取知识库列表',
      method: 'GET',
      endpoint: '/api/v1/knowledge'
    }
  ];
  
  for (const test of tests) {
    await debugRequest(test.method, test.endpoint, test.data);
  }
}

async function runSystemAdminTests() {
  console.log('\n' + '★'.repeat(30));
  console.log('系统管理端应用测试');
  console.log('★'.repeat(30));
  
  const tests = [
    {
      name: '系统管理员登录',
      method: 'POST',
      endpoint: '/api/v1/auth/login',
      data: { email: 'admin@system.com', password: 'admin123' }
    },
    {
      name: '获取所有企业列表',
      method: 'GET',
      endpoint: '/api/v1/admin/enterprises'
    },
    {
      name: '获取API配置',
      method: 'GET',
      endpoint: '/api/v1/admin/api-config'
    },
    {
      name: '获取系统统计',
      method: 'GET',
      endpoint: '/api/v1/admin/stats'
    }
  ];
  
  for (const test of tests) {
    await debugRequest(test.method, test.endpoint, test.data);
  }
}

async function main() {
  console.log('================================================');
  console.log('RAG智能客服系统 - 前端API联合调试');
  console.log('================================================');
  console.log(`API Base URL: ${API_BASE_URL}`);
  
  const args = process.argv.slice(2);
  const testAll = args.includes('--all');
  const testConsumer = args.includes('--consumer');
  const testEnterprise = args.includes('--enterprise');
  const testAdmin = args.includes('--admin');
  
  if (testAll || (!testConsumer && !testEnterprise && !testAdmin)) {
    await runConsumerAppTests();
    await runEnterpriseAppTests();
    await runSystemAdminTests();
  } else {
    if (testConsumer) await runConsumerAppTests();
    if (testEnterprise) await runEnterpriseAppTests();
    if (testAdmin) await runSystemAdminTests();
  }
  
  console.log('\n================================================');
  console.log('调试完成');
  console.log('================================================');
}

main().catch(console.error);
