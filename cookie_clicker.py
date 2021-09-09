"""
Cookie Clicker Simulator
Must be run through the CodeSkulptor IDE at https://py3.codeskulptor.org/
to make use of local dependencies.
"""

import poc_clicker_provided as provided
import simpleplot
import math
import codeskulptor

# Used to increase the timeout, if necessary
codeskulptor.set_timeout(20)

# Constants
SIM_TIME = 10000000000.0


class ClickerState:
    """
    Simple class to keep track of the game state.
    """
    
    def __init__(self):
        self._total_cookies = 0.0
        self._current_cookies = 0.0
        self._current_time = 0.0
        self._cps = 1.0
        self._history = [(0.0, None, 0.0, 0.0)]
        
    def __str__(self):
        """
        Return human readable state
        """
        ret_str = ''
        ret_str += 'Total cookies: ' + str(self._total_cookies) + '\n'
        ret_str += 'Current cookies: ' + str(self._current_cookies) + '\n'
        ret_str += 'Current time: ' + str(self._current_time) + '\n'
        ret_str += 'CPS: ' + str(self._cps) + '\n'
        ret_str += 'History: (length)' + str(len(self._history)) + str(self._history)
        return ret_str
        
    def get_cookies(self):
        """
        Return current number of cookies 
        (not total number of cookies)
        
        Should return a float
        """
        return self._current_cookies
    
    def get_cps(self):
        """
        Get current CPS

        Should return a float
        """
        return self._cps
    
    def get_time(self):
        """
        Get current time

        Should return a float
        """
        return self._current_time
    
    def get_history(self):
        """
        Return history list

        History list should be a list of tuples of the form:
        (time, item, cost of item, total cookies)

        For example: [(0.0, None, 0.0, 0.0)]

        Should return a copy of any internal data structures,
        so that they will not be modified outside of the class.
        """
        hist = self._history[:]
        return hist

    def time_until(self, cookies):
        """
        Return time until you have the given number of cookies
        (could be 0.0 if you already have enough cookies)

        Should return a float with no fractional part
        """
        if cookies <= self.get_cookies():
            return 0.0
        time_to_wait = math.ceil((cookies - self.get_cookies()) / self.get_cps())
        return time_to_wait
    
    def wait(self, time):
        """
        Wait for given amount of time and update state

        Should do nothing if time <= 0.0
        """
        if time <= 0.0:
            pass
        else:
            # time = math.ceil(time)
            self._current_time += time
            new_cookies = self.get_cps() * time
            self._current_cookies += new_cookies
            self._total_cookies += new_cookies
    
    def buy_item(self, item_name, cost, additional_cps):
        """
        Buy an item and update state

        Should do nothing if you cannot afford the item
        """
        if cost > self.get_cookies():
            return
        else:
            self._current_cookies = self._current_cookies - cost
            self._cps += additional_cps
            self._history.append((self.get_time(), item_name, cost, self._total_cookies))

    
def simulate_clicker(build_info, duration, strategy):
    """
    Function to run a Cookie Clicker game for the given
    duration with the given strategy.  Returns a ClickerState
    object corresponding to the final state of the game.
    """
    # make clone of build_info object
    build_info_clone = build_info.clone()
    # create new clickerstate obj
    cso = ClickerState()
    # loop until time in clickerstate reaches simulation duration
    while True:
        # check the current time and break out of loop if duration passed
        if cso.get_time() > duration:
            break
        # call strategy function to determine next item to purchase
        time_left = duration - cso.get_time()
        next_purchase = strategy(cso.get_cookies(), cso.get_cps(), cso.get_history(), time_left, build_info_clone)
        # break out of loop if strategy returns None
        if next_purchase is None:
            break
        # get wait time until next possible purchase
        wait_time = cso.time_until(build_info_clone.get_cost(next_purchase))
        # if wait is finishes after simulation duration break out of loop
        wait_to = cso.get_time() + wait_time
        if wait_to > duration:
            break
        # wait until the right time
        if wait_time == 0:
            pass
        else:
            # check if wait fun argument is time to wait to or time to wait
            cso.wait(wait_time)
        # buy the item
        cso.buy_item(next_purchase, build_info_clone.get_cost(next_purchase), build_info_clone.get_cps(next_purchase))
        # udate the build info
        build_info_clone.update_item(next_purchase)
    # allow any time left to go past
    cso.wait(duration - cso.get_time())
    # at final duration time, allow any purchases 
    while True:
        time_left = duration - cso.get_time()
        next_purchase = strategy(cso.get_cookies(), cso.get_cps(), cso.get_history(), time_left, build_info_clone)
        if next_purchase is None:
            break
        elif cso.get_cookies() >= build_info_clone.get_cost(next_purchase):
            cso.buy_item(next_purchase, build_info_clone.get_cost(next_purchase), 
                         build_info_clone.get_cps(next_purchase))
        else:
            break
    return cso


def strategy_cursor_broken(cookies, cps, history, time_left, build_info):
    """
    Always pick Cursor!

    Note that this simplistic (and broken) strategy does not properly
    check whether it can actually buy a Cursor in the time left.  Your
    simulate_clicker function must be able to deal with such broken
    strategies.  Further, your strategy functions must correctly check
    if you can buy the item in the time left and return None if you
    can't.
    """
    return "Cursor"


def strategy_none(cookies, cps, history, time_left, build_info):
    """
    Always return None

    This is a pointless strategy that will never buy anything, but
    that you can use to help debug your simulate_clicker function.
    """
    return None


def strategy_cheap(cookies, cps, history, time_left, build_info):
    """
    Always buy the cheapest item you can afford in the time left.
    """
    potential_cookies = time_left / cps
    # get available items
    # get costs for available items
    available_items = []
    for item in build_info.build_items():
        if build_info.get_cost(item) <= potential_cookies:
            available_items.append((build_info.get_cost(item), item))
    
    # make list of items available within cookie price range
    # if no item available, return None
    if len(available_items) == 0:
        return None
    # return cheapest item
    else:
        return sorted(available_items, key=lambda d_x: d_x[0])[0][1]


def strategy_expensive(cookies, cps, history, time_left, build_info):
    """
    Always buy the most expensive item you can afford in the time left.
    """
    potential_cookies = cookies + (time_left * cps)
    # get available items
    # get costs for available items
    available_items = []
    for item in build_info.build_items():
        if build_info.get_cost(item) <= potential_cookies:
            available_items.append((build_info.get_cost(item), item))
    
    # make list of items available within cookie price range
    # if no item available, return None
    if len(available_items) == 0:
        return None
    # return most expensive item
    else:
        return sorted(available_items, key=lambda d_x: d_x[0], reverse=True)[0][1]


def max_item_purchase(item, time_left, cost, build_info):
    """
    Returns the maximum number of one item type that can be purchased
    in the time left.
    """
    b_i = build_info.clone()
    counter = 0
    cost = cost
    time_left = time_left
    while time_left >= cost:
        cost = b_i.get_cost(item)
        b_i.update_item(item)
        time_left -= cost
        counter += 1
    return counter


def cps_return(no_of_purchases, cps):
    """
    Returns the increase of cps achieved with maximum purchase of one item.
    """
    return no_of_purchases * cps


def strategy_best(cookies, cps, history, time_left, build_info):
    """
    The best strategy that you are able to implement.
    """
    potential_cookies = cookies + (time_left * cps)
    available_items = []
    for item in build_info.build_items():
        available_items.append((build_info.get_cost(item) / build_info.get_cps(item), item))
    
    # make list of items available within cookie price range
    # if no item available, return None
    if len(available_items) == 0:
        return None
    # return most expensive item
    else:
        return sorted(available_items, key=lambda d_x: d_x[0], reverse=True)[0][1]
    
        
def run_strategy(strategy_name, time, strategy):
    """
    Run a simulation for the given time with one strategy.
    """
    state = simulate_clicker(provided.BuildInfo(), time, strategy)

    # Plot total cookies over time

    # Uncomment out the lines below to see a plot of total cookies vs. time
    # Be sure to allow popups, if you do want to see it

    history = state.get_history()
    history = [(item[0], item[3]) for item in history]
    simpleplot.plot_lines(strategy_name, 1000, 400, 'Time', 'Total Cookies', [history], True)


def run():
    """
    Run the simulator.
    """    
    # run_strategy("Cursor", SIM_TIME, strategy_cursor_broken)

    # Add calls to run_strategy to run additional strategies
    
    # run_strategy("Cheap", SIM_TIME, strategy_cheap)
    # run_strategy("Expensive", SIM_TIME, strategy_expensive)
    # run_strategy("Expensive2", 5.0, strategy_expensive)
    run_strategy("Best", SIM_TIME, strategy_best)
    

run()
