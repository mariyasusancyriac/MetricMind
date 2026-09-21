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
    quarter: { sql: `quarter`, type: `string` },
    region: { sql: `region`, type: `string` },
    product_line: { sql: `product_line`, type: `string` }
  },

  measures: {
    total_revenue: { sql: `gross_revenue`, type: `sum` },
    total_cogs: { sql: `cogs`, type: `sum` },
    total_operating_expense: { sql: `operating_expense`, type: `sum` },
    net_margin: {
      sql: `${CUBE.total_revenue} - (${CUBE.total_cogs} + ${CUBE.total_operating_expense})`,
      type: `number`
    },
    profit_margin_pct: {
      sql: `(${CUBE.net_margin} / NULLIF(${CUBE.total_revenue}, 0)) * 100`,
      type: `number`
    }
  }
});