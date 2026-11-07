import './style.css'
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ledgerline_token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

interface User {
  id: number
  name: string
  email: string
  role?: string
}

interface Account {
  id: number
  account_number: string
  account_type: string
  balance: string
  currency: string
  status: string
}

interface LedgerEntry {
  account_id: number
  entry_type: string
  amount: string
}

interface Transaction {
  transaction_id: number
  reference_id: string
  transaction_type: string
  amount: string
  status: string
  description: string
  created_at: string
  entries: LedgerEntry[]
}

let currentUser: User | null = null
let accounts: Account[] = []
let transactions: Transaction[] = []
let activeSection = 'overview'
let authMode: 'login' | 'register' = 'login'
let selectedAccountId: number | null = null

const app = document.querySelector<HTMLDivElement>('#app')!

function escapeHtml(value: unknown): string {
  return String(value ?? '').replace(/[&<>"']/g, (char) => {
    const entities: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    }
    return entities[char]
  })
}

function money(value: string | number, currency = 'INR'): string {
  const amount = Number(value)

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number.isFinite(amount) ? amount : 0)
}

function formatDate(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return '—'

  return date.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function showToast(message: string, type: 'success' | 'error' = 'success') {
  const oldToast = document.querySelector('.toast')
  oldToast?.remove()

  const toast = document.createElement('div')
  toast.className = `toast ${type}`
  toast.textContent = message

  document.body.appendChild(toast)

  window.setTimeout(() => toast.remove(), 3500)
}

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return (
      error.response?.data?.error ||
      error.response?.data?.message ||
      error.message ||
      'Something went wrong'
    )
  }

  return error instanceof Error ? error.message : 'Something went wrong'
}

function makeIdempotencyKey(): string {
  if (crypto.randomUUID) {
    return crypto.randomUUID()
  }

  return `ledgerline-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function transactionIcon(type: string): string {
  switch (type.toLowerCase()) {
    case 'deposit':
      return '↓'
    case 'withdrawal':
      return '↑'
    case 'transfer':
      return '⇄'
    default:
      return '↔'
  }
}

function transactionLabel(type: string): string {
  switch (type.toLowerCase()) {
    case 'deposit':
      return 'Deposit'
    case 'withdrawal':
      return 'Withdrawal'
    case 'transfer':
      return 'Transfer'
    default:
      return type
  }
}

function transactionRows(items: Transaction[]): string {
  if (!items.length) {
    return `
      <tr>
        <td colspan="5" class="empty-cell">
          No transactions yet. Your activity will appear here.
        </td>
      </tr>
    `
  }

  return items.map((item) => {
    const type = item.transaction_type.toLowerCase()
    const isCredit = item.entries.some(
      (entry) => entry.entry_type.toLowerCase() === 'credit'
    )

    const sign =
      type === 'deposit'
        ? '+'
        : type === 'withdrawal'
          ? '-'
          : isCredit
            ? '+'
            : '-'

    const amountClass = sign === '+' ? 'positive' : 'negative'

    return `
      <tr>
        <td>
          <div class="transaction-name">
            <span class="transaction-icon ${type}">
              ${transactionIcon(type)}
            </span>
            <div>
              <strong>${escapeHtml(transactionLabel(type))}</strong>
              <small>${escapeHtml(item.description || 'Money movement')}</small>
            </div>
          </div>
        </td>
        <td class="reference">${escapeHtml(item.reference_id)}</td>
        <td>${escapeHtml(formatDate(item.created_at))}</td>
        <td>
          <span class="status-pill">${escapeHtml(item.status)}</span>
        </td>
        <td class="amount ${amountClass}">
          ${sign}${money(item.amount)}
        </td>
      </tr>
    `
  }).join('')
}

function renderAuth(): void {
  const isRegister = authMode === 'register'

  app.innerHTML = `
    <main class="auth-page">
      <section class="auth-brand">
        <div class="brand-mark">L</div>
        <h1>LedgerLine</h1>
        <p class="brand-tagline">
          Money movement you can trust.
        </p>

        <div class="auth-feature">
          <span class="feature-symbol">↔</span>
          <div>
            <strong>Every transaction matters.</strong>
            <p>Secure transfers, reliable balances and a ledger you can verify.</p>
          </div>
        </div>

        <div class="auth-feature">
          <span class="feature-symbol">✓</span>
          <div>
            <strong>Built for accountability.</strong>
            <p>Every money movement is recorded and traceable.</p>
          </div>
        </div>

        <div class="auth-footer">LEDGERLINE · SECURE DIGITAL BANKING</div>
      </section>

      <section class="auth-panel">
        <div class="auth-card">
          <div class="mobile-brand">
            <div class="brand-mark">L</div>
            <strong>LedgerLine</strong>
          </div>

          <span class="eyebrow">${isRegister ? 'GET STARTED' : 'WELCOME BACK'}</span>
          <h2>${isRegister ? 'Create your account' : 'Sign in to LedgerLine'}</h2>
          <p class="muted">
            ${
              isRegister
                ? 'Register to start managing your money.'
                : 'Enter your credentials to access your dashboard.'
            }
          </p>

          <form id="auth-form" class="form-stack">
            ${
              isRegister
                ? `
                  <label>
                    Full name
                    <input
                      name="name"
                      type="text"
                      placeholder="Enter your full name"
                      required
                    />
                  </label>
                `
                : ''
            }

            <label>
              Email address
              <input
                name="email"
                type="email"
                placeholder="you@example.com"
                required
              />
            </label>

            <label>
              Password
              <input
                name="password"
                type="password"
                placeholder="At least 8 characters"
                minlength="${isRegister ? 8 : 1}"
                required
              />
            </label>

            <button class="primary-button full-button" type="submit">
              ${isRegister ? 'Create account' : 'Sign in'}
              <span>→</span>
            </button>
          </form>

          <p class="auth-switch">
            ${
              isRegister
                ? 'Already have an account?'
                : "Don't have an account?"
            }
            <button id="switch-auth" class="text-button">
              ${isRegister ? 'Sign in' : 'Create account'}
            </button>
          </p>

          <p class="auth-note">
            Your account access is protected by JWT authentication.
          </p>
        </div>
      </section>
    </main>
  `

  document.querySelector<HTMLFormElement>('#auth-form')
    ?.addEventListener('submit', handleAuthSubmit)

  document.querySelector<HTMLButtonElement>('#switch-auth')
    ?.addEventListener('click', () => {
      authMode = isRegister ? 'login' : 'register'
      renderAuth()
    })
}

async function handleAuthSubmit(event: SubmitEvent): Promise<void> {
  event.preventDefault()

  const form = event.currentTarget as HTMLFormElement
  const formData = new FormData(form)
  const button = form.querySelector<HTMLButtonElement>('button[type="submit"]')

  const email = String(formData.get('email') || '').trim()
  const password = String(formData.get('password') || '')

  if (!email || !password) {
    showToast('Please enter your email and password.', 'error')
    return
  }

  if (button) {
    button.disabled = true
    button.textContent = 'Please wait...'
  }

  try {
    if (authMode === 'register') {
      const name = String(formData.get('name') || '').trim()

      await api.post('/auth/register', {
        name,
        email,
        password,
      })

      showToast('Registration successful. Please sign in.')
      authMode = 'login'
      renderAuth()
      return
    }

    const response = await api.post('/auth/login', {
      email,
      password,
    })

    localStorage.setItem('ledgerline_token', response.data.access_token)

    currentUser = response.data.user
    await loadDashboard()
  } catch (error) {
    showToast(getErrorMessage(error), 'error')
  } finally {
    if (button && button.isConnected) {
      button.disabled = false
      button.textContent = authMode === 'register'
        ? 'Create account'
        : 'Sign in'
    }
  }
}

async function loadDashboard(): Promise<void> {
  try {
    const [profileResponse, accountResponse, transactionResponse] =
      await Promise.all([
        api.get('/auth/profile'),
        api.get('/accounts/'),
        api.get('/transactions/'),
      ])

    currentUser = profileResponse.data
    accounts = accountResponse.data.accounts || []
    transactions = transactionResponse.data.transactions || []

    if (
      selectedAccountId === null ||
      !accounts.some((account) => account.id === selectedAccountId)
    ) {
      selectedAccountId = accounts[0]?.id ?? null
    }

    renderDashboard()
  } catch (error) {
    const message = getErrorMessage(error)

    if (
      axios.isAxiosError(error) &&
      (error.response?.status === 401 || error.response?.status === 422)
    ) {
      logout(false)
      showToast('Your session expired. Please sign in again.', 'error')
      return
    }

    showToast(message, 'error')
    renderDashboard()
  }
}

function renderDashboard(): void {
  if (!currentUser) {
    renderAuth()
    return
  }

  const totalBalance = accounts.reduce(
    (total, account) => total + Number(account.balance || 0),
    0
  )

  
  const content = renderSectionContent()

  app.innerHTML = `
    <div class="dashboard-shell">
      <aside class="sidebar">
        <div class="sidebar-brand">
          <div class="brand-mark">L</div>
          <div>
            <strong>LedgerLine</strong>
            <small>Digital Banking</small>
          </div>
        </div>

        <div class="sidebar-label">WORKSPACE</div>

        <nav class="side-nav">
          <button class="nav-item ${activeSection === 'overview' ? 'active' : ''}" data-section="overview">
            <span>▦</span> Overview
          </button>
          <button class="nav-item ${activeSection === 'transactions' ? 'active' : ''}" data-section="transactions">
            <span>↔</span> Transactions
          </button>
          <button class="nav-item ${activeSection === 'deposit' ? 'active' : ''}" data-section="deposit">
            <span>↓</span> Deposit
          </button>
          <button class="nav-item ${activeSection === 'withdraw' ? 'active' : ''}" data-section="withdraw">
            <span>↑</span> Withdraw
          </button>
          <button class="nav-item ${activeSection === 'transfer' ? 'active' : ''}" data-section="transfer">
            <span>⇄</span> Transfer
          </button>
        </nav>

        <div class="sidebar-bottom">
          <div class="security-card">
            <span>✓</span>
            <strong>Secure by design</strong>
            <small>Transactions are recorded in your ledger.</small>
          </div>

          <button id="logout-button" class="logout-button">
            <span>↪</span> Sign out
          </button>
        </div>
      </aside>

      <main class="main-area">
        <header class="topbar">
          <div>
            <span class="eyebrow">YOUR FINANCIAL SPACE</span>
            <h1>${escapeHtml(sectionTitle())}</h1>
          </div>

          <div class="profile-area">
            <div class="profile-avatar">
              ${escapeHtml(currentUser.name.charAt(0).toUpperCase())}
            </div>
            <div class="profile-info">
              <strong>${escapeHtml(currentUser.name)}</strong>
              <small>${escapeHtml(currentUser.email)}</small>
            </div>
          </div>
        </header>

        <section class="page-content">
          ${
            activeSection === 'overview'
              ? `
                <div class="welcome-row">
                  <div>
                    <h2>Good day, ${escapeHtml(currentUser.name.split(' ')[0])} 👋</h2>
                    <p class="muted">Here's what's happening with your accounts.</p>
                  </div>
                  <button id="refresh-button" class="secondary-button">↻ Refresh</button>
                </div>

                <div class="stats-grid">
                  <article class="stat-card balance-card">
                    <div class="stat-heading">
                      <span>Total balance</span>
                      <span class="stat-icon">₹</span>
                    </div>
                    <h2>${money(totalBalance)}</h2>
                    <p>Across ${accounts.length} account${accounts.length === 1 ? '' : 's'}</p>
                  </article>

                  <article class="stat-card">
                    <div class="stat-heading">
                      <span>Bank accounts</span>
                      <span class="stat-icon">▣</span>
                    </div>
                    <h2>${accounts.length}</h2>
                    <p>Active accounts</p>
                  </article>

                  <article class="stat-card">
                    <div class="stat-heading">
                      <span>Transactions</span>
                      <span class="stat-icon">↔</span>
                    </div>
                    <h2>${transactions.length}</h2>
                    <p>Latest recorded activity</p>
                  </article>
                </div>

                <div class="content-grid">
                  <section class="panel accounts-panel">
                    <div class="panel-heading">
                      <div>
                        <h3>Your accounts</h3>
                        <p>Manage your bank accounts</p>
                      </div>
                      <button id="create-account-button" class="small-primary">
                        + New account
                      </button>
                    </div>

                    ${
                      accounts.length
                        ? accounts.map((account) => `
                          <button
                            class="account-card ${selectedAccountId === account.id ? 'selected' : ''}"
                            data-account-id="${account.id}"
                          >
                            <div class="account-top">
                              <span class="account-type">${escapeHtml(account.account_type)} account</span>
                              <span class="account-status">${escapeHtml(account.status)}</span>
                            </div>
                            <strong>${money(account.balance, account.currency)}</strong>
                            <small>${escapeHtml(account.account_number)}</small>
                            <span class="account-id">Account ID: ${account.id}</span>
                          </button>
                        `).join('')
                        : `
                          <div class="empty-state">
                            <div class="empty-icon">▣</div>
                            <strong>No bank account yet</strong>
                            <p>Create an account to start using LedgerLine.</p>
                            <button id="empty-create-account" class="primary-button">
                              Create bank account
                            </button>
                          </div>
                        `
                    }
                  </section>

                  <section class="panel quick-panel">
                    <div class="panel-heading">
                      <div>
                        <h3>Quick actions</h3>
                        <p>Move money with ease</p>
                      </div>
                    </div>

                    <div class="quick-actions">
                      <button class="quick-action" data-section="deposit">
                        <span class="quick-icon deposit-icon">↓</span>
                        <strong>Deposit</strong>
                        <small>Add money</small>
                      </button>
                      <button class="quick-action" data-section="withdraw">
                        <span class="quick-icon withdraw-icon">↑</span>
                        <strong>Withdraw</strong>
                        <small>Take out money</small>
                      </button>
                      <button class="quick-action" data-section="transfer">
                        <span class="quick-icon transfer-icon">⇄</span>
                        <strong>Transfer</strong>
                        <small>Send money</small>
                      </button>
                    </div>

                    <div class="ledger-note">
                      <span>✓</span>
                      <div>
                        <strong>Ledger-backed transactions</strong>
                        <p>Each completed money movement creates ledger entries and an audit record.</p>
                      </div>
                    </div>
                  </section>
                </div>

                ${renderRecentTransactions()}
              `
              : content
          }
        </section>
      </main>
    </div>
  `

  attachDashboardEvents()
}

function sectionTitle(): string {
  const titles: Record<string, string> = {
    overview: 'Dashboard',
    transactions: 'Transactions',
    deposit: 'Deposit money',
    withdraw: 'Withdraw money',
    transfer: 'Transfer money',
  }

  return titles[activeSection] || 'Dashboard'
}

function renderRecentTransactions(): string {
  return `
    <section class="panel transactions-panel">
      <div class="panel-heading">
        <div>
          <h3>Recent transactions</h3>
          <p>Your latest money movements</p>
        </div>
        <button class="text-button" data-section="transactions">
          View all →
        </button>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Transaction</th>
              <th>Reference</th>
              <th>Date</th>
              <th>Status</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>${transactionRows(transactions.slice(0, 5))}</tbody>
        </table>
      </div>
    </section>
  `
}

function renderSectionContent(): string {
  if (activeSection === 'transactions') {
    return `
      <section class="panel transactions-panel full-panel">
        <div class="panel-heading">
          <div>
            <h3>Transaction history</h3>
            <p>Your latest ${transactions.length} recorded transactions</p>
          </div>
          <button id="refresh-button" class="secondary-button">↻ Refresh</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Transaction</th>
                <th>Reference</th>
                <th>Date</th>
                <th>Status</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>${transactionRows(transactions)}</tbody>
          </table>
        </div>
      </section>
    `
  }

  if (activeSection === 'deposit' || activeSection === 'withdraw') {
    const isDeposit = activeSection === 'deposit'

    return `
      <section class="form-page">
        <div class="form-intro">
          <div class="large-action-icon ${isDeposit ? 'deposit-icon' : 'withdraw-icon'}">
            ${isDeposit ? '↓' : '↑'}
          </div>
          <h2>${isDeposit ? 'Add money to your account' : 'Withdraw from your account'}</h2>
          <p class="muted">
            ${
              isDeposit
                ? 'Record a deposit and update your account ledger.'
                : 'Withdraw money securely from your available balance.'
            }
          </p>
        </div>

        ${
          accounts.length
            ? `
              <form id="money-form" class="panel money-form">
                <label>
                  Select account
                  <select name="account_id" required>
                    ${accounts.map((account) => `
                      <option value="${account.id}" ${account.id === selectedAccountId ? 'selected' : ''}>
                        ${escapeHtml(account.account_number)} · ${money(account.balance)}
                      </option>
                    `).join('')}
                  </select>
                </label>

                <label>
                  Amount (INR)
                  <div class="amount-input">
                    <span>₹</span>
                    <input name="amount" type="number" min="0.01" max="9999999999999.99" step="0.01" placeholder="0.00" required />
                  </div>
                </label>

                <label>
                  Description
                  <input name="description" type="text" maxlength="200" placeholder="${isDeposit ? 'Salary, cash deposit...' : 'Reason for withdrawal...'}" />
                </label>

                <div class="form-info">
                  <span>✓</span>
                  Your transaction will be recorded with an idempotency key.
                </div>

                <button type="submit" class="primary-button full-button">
                  ${isDeposit ? 'Confirm deposit' : 'Confirm withdrawal'} →
                </button>
              </form>
            `
            : `
              <div class="panel empty-state">
                <strong>Create a bank account first</strong>
                <p>You need an active account before you can ${isDeposit ? 'deposit' : 'withdraw'} money.</p>
                <button id="create-account-button" class="primary-button">Create account</button>
              </div>
            `
        }
      </section>
    `
  }

  if (activeSection === 'transfer') {
    return `
      <section class="form-page">
        <div class="form-intro">
          <div class="large-action-icon transfer-icon">⇄</div>
          <h2>Send money securely</h2>
          <p class="muted">Transfer funds from your account to another LedgerLine account.</p>
        </div>

        ${
          accounts.length
            ? `
              <form id="transfer-form" class="panel money-form">
                <label>
                  From account
                  <select name="sender_account_id" required>
                    ${accounts.map((account) => `
                      <option value="${account.id}" ${account.id === selectedAccountId ? 'selected' : ''}>
                        ${escapeHtml(account.account_number)} · ${money(account.balance)}
                      </option>
                    `).join('')}
                  </select>
                </label>

                <label>
                  Receiver account ID
                  <input name="receiver_account_id" type="number" min="1" placeholder="Enter receiver's account ID" required />
                  <small class="field-help">Use the numeric account ID shared by the recipient.</small>
                </label>

                <label>
                  Amount (INR)
                  <div class="amount-input">
                    <span>₹</span>
                    <input name="amount" type="number" min="0.01" max="9999999999999.99" step="0.01" placeholder="0.00" required />
                  </div>
                </label>

                <label>
                  Description
                  <input name="description" type="text" maxlength="200" placeholder="What's this transfer for?" />
                </label>

                <div class="form-info">
                  <span>✓</span>
                  The sender and receiver ledger entries are recorded together.
                </div>

                <button type="submit" class="primary-button full-button">
                  Transfer money →
                </button>
              </form>
            `
            : `
              <div class="panel empty-state">
                <strong>Create a bank account first</strong>
                <p>You need an active account before you can transfer money.</p>
                <button id="create-account-button" class="primary-button">Create account</button>
              </div>
            `
        }
      </section>
    `
  }

  return ''
}

function attachDashboardEvents(): void {
  document.querySelectorAll<HTMLElement>('[data-section]').forEach((element) => {
    element.addEventListener('click', () => {
      const section = element.dataset.section

      if (section) {
        activeSection = section
        renderDashboard()
      }
    })
  })

  document.querySelectorAll<HTMLButtonElement>('[data-account-id]').forEach((button) => {
    button.addEventListener('click', () => {
      selectedAccountId = Number(button.dataset.accountId)
      renderDashboard()
    })
  })

  document.querySelector<HTMLButtonElement>('#logout-button')
    ?.addEventListener('click', () => logout())

  document.querySelector<HTMLButtonElement>('#refresh-button')
    ?.addEventListener('click', async () => {
      await loadDashboard()
      showToast('Dashboard refreshed.')
    })

  document.querySelector<HTMLButtonElement>('#create-account-button')
    ?.addEventListener('click', createAccount)

  document.querySelector<HTMLButtonElement>('#empty-create-account')
    ?.addEventListener('click', createAccount)

  document.querySelector<HTMLFormElement>('#money-form')
    ?.addEventListener('submit', handleMoneySubmit)

  document.querySelector<HTMLFormElement>('#transfer-form')
    ?.addEventListener('submit', handleTransferSubmit)
}

async function createAccount(): Promise<void> {
  try {
    const response = await api.post('/accounts/', {})
    selectedAccountId = response.data.account.id
    activeSection = 'overview'

    await loadDashboard()
    showToast('Bank account created successfully.')
  } catch (error) {
    showToast(getErrorMessage(error), 'error')
  }
}

async function handleMoneySubmit(event: SubmitEvent): Promise<void> {
  event.preventDefault()

  const form = event.currentTarget as HTMLFormElement
  const formData = new FormData(form)
  const button = form.querySelector<HTMLButtonElement>('button[type="submit"]')

  const accountId = Number(formData.get('account_id'))
  const amount = Number(formData.get('amount'))
  const description = String(formData.get('description') || '').trim()

  if (!accountId || !Number.isFinite(amount) || amount <= 0) {
    showToast('Enter a valid account and amount.', 'error')
    return
  }

  const isDeposit = activeSection === 'deposit'
  const endpoint = isDeposit ? '/transactions/deposit' : '/transactions/withdraw'

  if (button) {
    button.disabled = true
    button.textContent = 'Processing...'
  }

  try {
    const response = await api.post(
      endpoint,
      {
        account_id: accountId,
        amount: amount.toFixed(2),
        description: description || (isDeposit ? 'Deposit' : 'Withdrawal'),
      },
      {
        headers: {
          'Idempotency-Key': makeIdempotencyKey(),
        },
      }
    )

    await loadDashboard()
    showToast(response.data.message || 'Transaction completed successfully.')
  } catch (error) {
    showToast(getErrorMessage(error), 'error')
  } finally {
    if (button && button.isConnected) {
      button.disabled = false
      button.textContent = isDeposit ? 'Confirm deposit →' : 'Confirm withdrawal →'
    }
  }
}

async function handleTransferSubmit(event: SubmitEvent): Promise<void> {
  event.preventDefault()

  const form = event.currentTarget as HTMLFormElement
  const formData = new FormData(form)
  const button = form.querySelector<HTMLButtonElement>('button[type="submit"]')

  const senderAccountId = Number(formData.get('sender_account_id'))
  const receiverAccountId = Number(formData.get('receiver_account_id'))
  const amount = Number(formData.get('amount'))
  const description = String(formData.get('description') || '').trim()

  if (
    !senderAccountId ||
    !receiverAccountId ||
    senderAccountId === receiverAccountId ||
    !Number.isFinite(amount) ||
    amount <= 0
  ) {
    showToast('Check the sender, receiver and amount.', 'error')
    return
  }

  if (button) {
    button.disabled = true
    button.textContent = 'Processing transfer...'
  }

  try {
    const response = await api.post(
      '/transactions/transfer',
      {
        sender_account_id: senderAccountId,
        receiver_account_id: receiverAccountId,
        amount: amount.toFixed(2),
        description: description || 'Money transfer',
      },
      {
        headers: {
          'Idempotency-Key': makeIdempotencyKey(),
        },
      }
    )

    await loadDashboard()
    showToast(response.data.message || 'Transfer completed successfully.')
  } catch (error) {
    showToast(getErrorMessage(error), 'error')
  } finally {
    if (button && button.isConnected) {
      button.disabled = false
      button.textContent = 'Transfer money →'
    }
  }
}

function logout(showMessage = true): void {
  localStorage.removeItem('ledgerline_token')

  currentUser = null
  accounts = []
  transactions = []
  selectedAccountId = null
  activeSection = 'overview'
  authMode = 'login'

  renderAuth()

  if (showMessage) {
    showToast('You have signed out.')
  }
}

async function startApp(): Promise<void> {
  const token = localStorage.getItem('ledgerline_token')

  if (!token) {
    renderAuth()
    return
  }

  try {
    const response = await api.get('/auth/profile')
    currentUser = response.data
    await loadDashboard()
  } catch {
    logout(false)
  }
}

startApp()