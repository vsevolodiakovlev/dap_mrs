import pandas as pd
from ridgeplot import ridgeplot
import kaleido

def available_payoffs(data_input, 
                      spec_name = 'default', 
                      A_name = 'Applicants', 
                      B_name = 'Reviewers',
                      units = 'Z-Score',
                      bins = None):

    """
    Plot the available payoffs for the Applicants and Reviewers.

    Parameters
    ----------
    data_input : DataFrame
        The DataFrame containing the data.
    spec_name : str
        Specification name. Used to find the relevant variables in data_input and name the graph files. Default is 'default'.
    A_name : str
        The label for applicants in the graphs. Default is 'Applicants'.
    B_name : str
        The label for reviewers in the graphs. Default is 'Reviewers'.
    units : str
        The payoff units. Default is 'Z-Score'.
    bins : int or None
        The number of bins for histogram binning or KDE if None. Default is None.

    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        The plotly figure object.

    """

    if units == 'Z-Score':
        A_payoff_name = spec_name + '_A_obs_u_z'
        B_payoff_name = spec_name + '_B_obs_u_z'
    else:
        A_payoff_name = spec_name + '_A_obs_u'
        B_payoff_name = spec_name + '_B_obs_u'

    fig = ridgeplot(samples=[data_input[A_payoff_name],
                        data_input[B_payoff_name]],
                        labels = [A_name, B_name],
                        colorscale = "viridis", 
                        nbins=bins,
                        colormode = "row-index",
                        opacity=0.6)
    fig.update_layout(
        height=560,
        width=800,
        font_size=16,
        plot_bgcolor="white",
        xaxis_gridcolor="rgba(0, 0, 0, 0.1)",
        yaxis_gridcolor="rgba(0, 0, 0, 0.1)",
        title="Available payoffs",
        xaxis_title=units,
        showlegend=False,
    )
    fig.write_image(spec_name + '_available_payoffs.pdf')

    fig.show()

    return fig


def observed_vs_dap(data_output,
                    spec_name = 'default', 
                    A_name = 'Applicants', 
                    B_name = 'Reviewers',
                    units = 'Z-Score',
                    bins = None):
    
    """
    Plot the observed payoffs vs. the A-Optimal payoffs for the Applicants and Reviewers.

    Parameters
    ----------
    data_output : DataFrame
        The DataFrame containing the data. 
    spec_name : str
        Specification name. Used to find the relevant variables in data_output and name the graph files. Default is 'default'.
    A_name : str
        The label for applicants in the graphs. Default is 'Applicants'.
    B_name : str
        The label for reviewers in the graphs. Default is 'Reviewers'.
    units : str
        The payoff units. Default is 'Z-Score'.
    bins : int or None
        The number of bins for histogram binning or KDE if None. Default is None.
        
    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        The plotly figure object.

    """

    if units == 'Z-Score':
        A_diff_name = spec_name + '_A_obs_u_z'
        B_diff_name = spec_name + '_B_obs_u_z'
    else:
        A_diff_name = spec_name + '_A_obs_u'
        B_diff_name = spec_name + '_B_obs_u'

    fig = ridgeplot(samples=[data_output[A_diff_name],
                        data_output[B_diff_name]],
                        labels = [A_name, B_name],
                        colorscale = "viridis", 
                        nbins=bins,
                        colormode = "row-index",
                        opacity=0.6)
    fig.update_layout(
        height=560,
        width=800,
        font_size=16,
        plot_bgcolor="white",
        xaxis_gridcolor="rgba(0, 0, 0, 0.1)",
        yaxis_gridcolor="rgba(0, 0, 0, 0.1)",
        title="Observed vs. A-Optimal",
        xaxis_title=units,
        showlegend=False,
    )
    fig.write_image(spec_name + '_obs_vs_dap.pdf')

    fig.show()

    return fig


def apparent_values(data_output,
                    spec_name = 'default',
                    A_name = 'Applicants',
                    A_bias_char_name = 'bias_char',
                    units = 'Z-Score',
                    bins = None):
    
    """
    Plot the Applicants' apparent values for the two groups of agents defined by the bias characteristic.
    
    Parameters
    ----------
    data_output : DataFrame
        The DataFrame containing the data.
    spec_name : str
        Specification name. Used to find the relevant variables in data_output and name the graph files. Default is 'default'.
    A_name : str
        The label for applicants in the graphs. Default is 'Applicants'.
    A_bias_char_name : str
        The name of the applicants' binary characteristic that the reviewers have a bias towards. Default is 'A_bias_char'.
    units : str
        The payoff units. Default is 'Z-Score'.
    bins : int or None
        The number of bins for histogram binning or KDE if None. Default is None.

    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        The plotly figure object.
    """

    if units == 'Z-Score':
        A_apparent_name = spec_name + '_A_apparent_v_z'
        A_apparent_corrected_name = spec_name + '_A_apparent_corrected_v_z'
    else:
        A_apparent_name = spec_name + '_A_apparent_v'
        A_apparent_corrected_name = spec_name + '_A_apparent_corrected_v'

    fig = ridgeplot(samples=[data_output[A_apparent_name][data_output[A_bias_char_name] == 0],
                             data_output[A_apparent_name][data_output[A_bias_char_name] == 1],
                             data_output[A_apparent_corrected_name][data_output[A_bias_char_name] == 0],
                             data_output[A_apparent_corrected_name][data_output[A_bias_char_name] == 1]],
                        labels = ['Biased: Group 0', 'Biased: Group 1', 'Corrected: Group 0', 'Corrected: Group 1'],
                        colorscale = "viridis",
                        nbins=bins,
                        colormode = "row-index",
                        opacity=0.6)
    fig.update_layout(
        height=560,
        width=800,
        font_size=16,
        plot_bgcolor="white",
        xaxis_gridcolor="rgba(0, 0, 0, 0.1)",
        yaxis_gridcolor="rgba(0, 0, 0, 0.1)",
        title= 'Apparent values of ' + A_name,
        xaxis_title=units,
        showlegend=False,
    )
    fig.write_image(spec_name + '_apparent_values.pdf')

    fig.show()

    return fig


def bias_effect(data_output,
                spec_name = 'default',
                A_name = 'Applicants',
                A_bias_char_name = 'bias_char',
                units = 'Z-Score',
                bins = None):
    
    """
    Plot the bias' effect on the payoffs of the Applicants for the two groups of agents defined by the bias characteristic.

    Parameters
    ----------
    data_output : DataFrame
        The DataFrame containing the data.
    spec_name : str
        Specification name. Used to find the relevant variables in data_output and name the graph files. Default is 'default'.
    A_name : str
        The label for applicants in the graphs. Default is 'Applicants'.
    A_bias_char_name : str
        The name of the applicants' binary characteristic that the reviewers have a bias towards. Default is 'A_bias_char'.
    units : str
        The payoff units. Default is 'Z-Score'.
    bins : int or None
        The number of bins for histogram binning or KDE if None. Default is None.

    Returns
    -------
    fig : plotly.graph_objs._figure.Figure
        The plotly figure object.

    """

    if units == 'Z-Score':
        samples = [data_output[spec_name + '_A_obs_u_z'][data_output[A_bias_char_name] == 0],
                   data_output[spec_name + '_A_obs_u_z'][data_output[A_bias_char_name] == 1],
                   data_output[spec_name + '_A_dap_u_z'][data_output[A_bias_char_name] == 0],
                   data_output[spec_name + '_A_dap_u_z'][data_output[A_bias_char_name] == 1],
                   data_output[spec_name + '_diff_A_z'][data_output[A_bias_char_name] == 0],
                   data_output[spec_name + '_diff_A_z'][data_output[A_bias_char_name] == 1]]
    else:
        samples = [data_output[spec_name + '_A_obs_u'][data_output[A_bias_char_name] == 0],
                   data_output[spec_name + '_A_obs_u'][data_output[A_bias_char_name] == 1],
                   data_output[spec_name + '_A_dap_u'][data_output[A_bias_char_name] == 0],
                   data_output[spec_name + '_A_dap_u'][data_output[A_bias_char_name] == 1]]

    fig = ridgeplot(samples=samples,
                        labels = ['Observed: Group 0', 'Observed: Group 1', 'DAP: Group 0', 'DAP: Group 1', 'Difference: Group 0', 'Difference: Group 1'],
                        colorscale = "viridis", 
                        nbins=bins,
                        colormode = "row-index",
                        opacity=0.6)
    fig.update_layout(
        height=560,
        width=800,
        font_size=16,
        plot_bgcolor="white",
        xaxis_gridcolor="rgba(0, 0, 0, 0.1)",
        yaxis_gridcolor="rgba(0, 0, 0, 0.1)",
        title="Bias' effect on the payoffs of " + A_name,
        xaxis_title=units,
        showlegend=False,
    )
    fig.write_image(spec_name + '_bias_effect.pdf')

    fig.show()

    return fig
