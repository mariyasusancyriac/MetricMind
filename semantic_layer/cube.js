// MetricMind Unified Semantic Configuration
// Bridges SalesCube and ExpensesCube to deliver governed business metrics

cube(`EnterpriseFinance`, {
  sql: `SELECT * FROM enterprise_data`,

  joins: {
    SalesCube: {
      relationship: `belongsTo`,
      sql: `${CUBE}.transaction_id = ${SalesCube}.transaction_id`
    },
    ExpensesCube: {
      relationship: `belongsTo`,
      sql: `${CUBE}.transaction_id = ${ExpensesCube}.transaction_id`
    }
  },

  dimensions: {
    quarter: {
      sql: `quarter`,
      type: `string`,
      description: `Fiscal reporting quarter (e.g., 2025-Q4)`
    },
    region: {
      sql: `region`,
      type: `string`,
      description: `Operating geographical market`
    },
    product_line: {
      sql: `product_line`,
      type: `string`,
      description: `Tiered product catalog offering`
    }
  },

  measures: {
    total_revenue: {
      sql: `gross_revenue`,
      type: `sum`,
      format: `currency`,
      description: `Gross billed income across transactions`
    },
    total_cogs: {
      sql: `cogs`,
      type: `sum`,
      format: `currency`,
      description: `Cost of Goods Sold`
    },
    total_operating_expense: {
      sql: `operating_expense`,
      type: `sum`,
      format: `currency`,
      description: `Operating expenditure overhead`
    },
    net_margin: {
      sql: `${CUBE.total_revenue} - (${CUBE.total_cogs} + ${CUBE.total_operating_expense})`,
      type: `number`,
      format: `currency`,
      description: `Governed net profit margin formula`
    },
    profit_margin_pct: {
      sql: `(${CUBE.net_margin} / NULLIF(${CUBE.total_revenue}, 0)) * 100`,
      type: `number`,
      format: `percent`,
      description: `Governed profit margin percentage ratio`
    }
  }
});