import LandingPage from '../workflows/onboardingActivation/LandingPage'
import OnboardingPage from '../workflows/onboardingActivation/OnboardingPage'
import DashboardPage from '../workflows/dailyEngagement/DashboardPage'
import RewardsPage from '../workflows/gamification/RewardsPage'
import ZClubPage from '../workflows/clubFormation/ZClubPage'
import ZKartPage from '../workflows/zkartPurchase/ZKartPage'
import AccountPage from '../workflows/accountManagement/AccountPage'
import TrackingPage from '../workflows/tracking/TrackingPage'
import EarnAdsPage from '../pages/EarnAdsPage'
import EarnPayBillsPage from '../pages/EarnPayBillsPage'
import EarnActionPage from '../pages/EarnActionPage'
import EarnActionChecklistPage from '../pages/EarnActionChecklistPage'
import EarnIndexPage from '../pages/EarnIndexPage'
import ProductDetailPage from '../pages/ProductDetailPage'
import CheckoutPage from '../pages/CheckoutPage'
import DailyPullPage from '../pages/DailyPullPage'

export const appRoutes = [
  { path: '/', Component: LandingPage },
  { path: '/onboarding', Component: OnboardingPage },
  { path: '/dashboard', Component: DashboardPage },
  { path: '/earn/ads', Component: EarnAdsPage },
  { path: '/earn/bills', Component: EarnPayBillsPage },
  { path: '/earn', Component: EarnIndexPage },
  { path: '/earn/:actionId/verify', Component: EarnActionChecklistPage },
  { path: '/earn/:actionId', Component: EarnActionPage },
  { path: '/daily-pull', Component: DailyPullPage },
  { path: '/zkart', Component: ZKartPage },
  { path: '/zkart/products/:productId', Component: ProductDetailPage },
  { path: '/zkart/checkout/:productId', Component: CheckoutPage },
  { path: '/club', Component: ZClubPage },
  { path: '/spend/:spendId', Component: EarnActionPage },
  { path: '/rewards', Component: RewardsPage },
  { path: '/account', Component: AccountPage },
  { path: '/tracking', Component: TrackingPage },
]
